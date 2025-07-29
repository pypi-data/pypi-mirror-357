# kashima/mapper/layers/beachballs.py
from __future__ import annotations
import base64
import io
import logging
from itertools import count

import numpy as np
import pandas as pd
import folium
from folium.features import CustomIcon

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from obspy.imaging.beachball import beach

from ._layer_base import MapLayer

logger = logging.getLogger(__name__)


class BeachballLayer(MapLayer):
    """
    Draw focal‑mechanism beachballs.

    Handles both return types of obspy.beach():
      • Figure  (modern versions)
      • PatchCollection  (older / mopad fallback)
    """

    _CACHE: dict[str, str] = {}
    _SKIPPED = count()

    def __init__(
        self,
        events_df: pd.DataFrame,
        *,
        size_by: str = "mag",
        show: bool = True,
    ):
        cols = [
            "mrr",
            "mtt",
            "mpp",
            "mrt",
            "mrp",
            "mtp",
            "latitude",
            "longitude",
            "event_id",
            size_by,
        ]
        df = events_df.dropna(subset=cols).copy()
        norm = np.linalg.norm(df[["mrr", "mtt", "mpp", "mrt", "mrp", "mtp"]], axis=1)
        self.df = df[norm > 0]  # drop zero tensors
        self.size_by = size_by
        self.show = show

    # ------------------------------------------------------------------
    def _render_icon(self, row) -> str | None:
        """Return data‑URI PNG or None on failure."""
        eid = row["event_id"]
        if eid in self._CACHE:
            return self._CACHE[eid]

        mt = [
            row["mrr"],
            row["mtt"],
            row["mpp"],
            row["mrt"],
            row["mrp"],
            row["mtp"],
        ]
        size_px = int(18 + 2 * (row[self.size_by] or 0))

        try:
            # Try the simple way first (modern ObsPy)
            fig_or_patch = beach(
                mt, size=size_px, linewidth=0.6, facecolor="k", edgecolor="k"
            )

            if isinstance(fig_or_patch, PatchCollection):
                # Older ObsPy: embed patch in a tiny figure
                fig = plt.figure(figsize=(size_px / 72, size_px / 72), dpi=72)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_axis_off()
                ax.add_collection(fig_or_patch)
                ax.set_aspect("equal", "box")
                ax.autoscale_view()
            else:
                fig = fig_or_patch  # already a Figure

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=72, transparent=True)
            plt.close(fig)

        except Exception as e:
            if next(self._SKIPPED) < 10:  # log first 10 issues only
                logger.warning("Skip beachball for %s: %s", eid, e)
            return None

        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        self._CACHE[eid] = uri
        return uri

    # ------------------------------------------------------------------
    def to_feature_group(self) -> folium.FeatureGroup:
        fg = folium.FeatureGroup(name="Beachballs", show=self.show)
        added = 0

        for _, r in self.df.iterrows():
            uri = self._render_icon(r)
            if uri is None:
                continue
            sz = int(18 + 2 * (r[self.size_by] or 0))
            icon = CustomIcon(uri, icon_size=(sz, sz), icon_anchor=(sz // 2, sz // 2))
            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                icon=icon,
                tooltip=f"Mw {r['mag']:.1f}" if np.isfinite(r["mag"]) else None,
            ).add_to(fg)
            added += 1

        logger.info(
            "Beachball layer: %d icons drawn, %d skipped.", added, next(self._SKIPPED)
        )
        return fg
