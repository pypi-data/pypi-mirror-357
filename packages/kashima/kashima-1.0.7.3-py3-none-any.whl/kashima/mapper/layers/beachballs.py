# kashima/mapper/layers/beachballs.py   •   2025‑06‑25
from __future__ import annotations
import base64
import io
import logging
from itertools import count
from typing import Dict

import numpy as np
import pandas as pd
import folium
from folium.features import CustomIcon

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from obspy.imaging.beachball import beach

logger = logging.getLogger(__name__)


class BeachballLayer:
    """
    Render focal‑mechanism beachballs as Folium markers **with pop‑ups**.

    *   Accepts any DataFrame that has latitude, longitude, mag,
        fault_style and the six tensor components.
    *   Automatically centres icon, encodes as data‑URI (no temp files).
    *   Caches icons per event_id to avoid recomputation when toggling.
    """

    _CACHE: Dict[str, str] = {}
    _warned = count()  # throttle matplotlib warnings

    def __init__(
        self,
        df: pd.DataFrame,
        *,
        show: bool = True,
        legend_map: dict[str, str] | None = None,
        size_by: str = "mag",
    ):
        # keep only rows with finite tensors
        cols = ["mrr", "mtt", "mpp", "mrt", "mrp", "mtp"]
        self.df = df.dropna(subset=cols).copy()
        self.show = show
        self.size_by = size_by
        self.legend_map = legend_map or {}

    # ------------------------------------------------------------------
    def _render_icon(self, r) -> str | None:
        eid = r["event_id"]
        if eid in self._CACHE:
            return self._CACHE[eid]

        mt = [r.mrr, r.mtt, r.mpp, r.mrt, r.mrp, r.mtp]
        size_px = int(18 + 2 * (r[self.size_by] or 0))

        try:
            fig_or_patch = beach(
                mt, size=size_px, linewidth=0.6, facecolor="k", edgecolor="k"
            )

            if isinstance(fig_or_patch, PatchCollection):
                fig = plt.figure(figsize=(size_px / 72, size_px / 72), dpi=72)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.set_axis_off()
                ax.add_collection(fig_or_patch)
                ax.set_aspect("equal")
                ax.autoscale_view()
            else:  # modern ObsPy returns a Figure
                fig = fig_or_patch

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=72, transparent=True)
            plt.close(fig)

        except Exception as e:
            if next(self._warned) < 10:
                logger.warning("Skip beachball for %s: %s", eid, e)
            return None

        uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        self._CACHE[eid] = uri
        return uri

    # ------------------------------------------------------------------
    def _make_popup(self, r) -> folium.Popup:
        lg = self.legend_map
        lines = [
            f"<b>{lg.get('mag','Magnitude')}:</b> {r.mag:.2f}",
            f"<b>{lg.get('fault_style','Fault Style')}:</b> {r.fault_style}",
            f"<b>{lg.get('latitude','Latitude')}:</b> {r.latitude:.4f}",
            f"<b>{lg.get('longitude','Longitude')}:</b> {r.longitude:.4f}",
        ]
        # show any other legend fields present in row
        for field, label in lg.items():
            if field in ("mag", "fault_style", "latitude", "longitude"):
                continue
            val = r.get(field)
            if pd.notnull(val):
                lines.append(f"<b>{label}:</b> {val}")
        return folium.Popup("<br>".join(lines), max_width=300)

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
                location=[r.latitude, r.longitude],
                icon=icon,
                tooltip=f"Mw {r.mag:.1f}" if np.isfinite(r.mag) else None,
                popup=self._make_popup(r),
            ).add_to(fg)
            added += 1

        logger.info("Beachball layer: %d icons drawn.", added)
        return fg
