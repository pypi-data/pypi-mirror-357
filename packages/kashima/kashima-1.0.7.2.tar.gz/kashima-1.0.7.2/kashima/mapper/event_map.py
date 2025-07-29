# kashima/mapper/event_map.py  —  COMPLETE REPLACEMENT
from __future__ import annotations
import logging
import math
from pathlib import Path
import folium
import branca
import pandas as pd

from .config import (
    MapConfig,
    EventConfig,
    FaultConfig,
    StationConfig,
    TILE_LAYER_CONFIGS,
)
from .utils import (
    great_circle_bbox,
    stream_read_csv_bbox,
    load_faults,
    load_stations_csv,
    calculate_distances_vectorized,
)
from .isc_catalog import load_isc
from .layers import (
    EventMarkerLayer,
    BeachballLayer,
    HeatmapLayer,
    FaultLayer,
    StationLayer,
    EpicentralCirclesLayer,
)

logger = logging.getLogger(__name__)


class EventMap:
    """
    Build an interactive Folium map with events, heatmap, beachballs,
    faults, stations, distance circles and all tile layers.

    Public constructor signature is unchanged from your original version.
    """

    # ────────────────────────────────────────────────────────────────
    def __init__(
        self,
        map_config: MapConfig,
        event_config: EventConfig,
        *,
        events_csv: str | Path,
        legend_csv: str | None = None,
        isc_csv: str | None = None,
        mandatory_mag_col: str = "mag",
        calculate_distance: bool = True,
        fault_config: FaultConfig | None = None,
        station_config: StationConfig | None = None,
        tooltip_fields: list[str] | None = None,
        log_level: int = logging.INFO,
    ):
        logger.setLevel(log_level)

        # configs
        self.mc = map_config
        self.ec = event_config
        self.fc = fault_config
        self.sc = station_config

        # paths
        self.events_csv = Path(events_csv)
        self.isc_csv = Path(isc_csv) if isc_csv else None
        self.legend_csv = Path(legend_csv) if legend_csv else None

        # options
        self.mandatory_mag_col = mandatory_mag_col
        self.calculate_distance = calculate_distance
        self.tooltip_fields = tooltip_fields or ["place"]

        # runtime containers
        self.events_df: pd.DataFrame = pd.DataFrame()
        self.faults_gdf = None
        self.stations_df = pd.DataFrame()
        self.color_map: branca.colormap.LinearColormap | None = None
        self.legend_map: dict[str, str] = {}

        self._loaded = False

    # =========================  PUBLIC  ==============================

    def load_data(self):
        """Back‑compat entry point."""
        if not self._loaded:
            self._load_everything()

    def get_map(self) -> folium.Map:
        """Return a ready Folium map (auto‑loads data if needed)."""
        if not self._loaded:
            self._load_everything()

        m = folium.Map(
            location=[self.mc.latitude, self.mc.longitude],
            zoom_start=self.mc.base_zoom_level,
            min_zoom=self.mc.min_zoom_level,
            max_zoom=self.mc.max_zoom_level,
            control_scale=True,
        )

        # ---- Layers ---------------------------------------------------
        EventMarkerLayer(
            self.events_df,
            mag_col=self.mandatory_mag_col,
            color_map=self.color_map,
            legend_map=self.legend_map,
            tooltip_fields=self.tooltip_fields,
            clustered=self.ec.show_cluster_default,
            show=self.ec.show_events_default,
        ).to_feature_group().add_to(m)

        BeachballLayer(
            self.events_df[
                self.events_df[self.mandatory_mag_col]
                >= (self.ec.beachball_min_magnitude or -np.inf)
            ],
            show=self.ec.show_beachballs_default,
        ).to_feature_group().add_to(m)

        HeatmapLayer(
            self.events_df,
            radius=self.ec.heatmap_radius,
            blur=self.ec.heatmap_blur,
            min_opacity=self.ec.heatmap_min_opacity,
            show=self.ec.show_heatmap_default,
        ).to_feature_group().add_to(m)

        if self.faults_gdf is not None:
            FaultLayer(
                self.faults_gdf,
                color=self.fc.regional_faults_color,
                weight=self.fc.regional_faults_weight,
                show=self.fc.include_faults,
            ).to_feature_group().add_to(m)

        if not self.stations_df.empty:
            StationLayer(self.stations_df).to_feature_group().add_to(m)

        EpicentralCirclesLayer(
            self.mc.latitude,
            self.mc.longitude,
            self.mc.radius_km,
            n_circles=self.mc.epicentral_circles,
            show=self.ec.show_epicentral_circles_default,
        ).to_feature_group().add_to(m)

        # ---- Base layers & UI ----------------------------------------
        self._add_tile_layers(m)
        folium.LayerControl().add_to(m)
        self._add_color_legend(m)

        return m

    # =========================  INTERNAL  ============================

    def _load_everything(self):
        logger.info("Loading catalogues and auxiliary data …")

        # 1) bounding box
        bbox = great_circle_bbox(
            self.mc.longitude,
            self.mc.latitude,
            self.mc.radius_km * (self.ec.event_radius_multiplier or 1.0),
        )
        # 2) read CSV(s)
        frames: list[pd.DataFrame] = []
        if self.events_csv.exists():
            frames.append(
                stream_read_csv_bbox(self.events_csv, bbox=bbox, parse_dates=["time"])
            )
        if self.isc_csv and self.isc_csv.exists():
            try:
                frames.append(load_isc(self.isc_csv, bbox=bbox))
            except TypeError:  # old signature
                df = load_isc(self.isc_csv)
                frames.append(df[df["latitude"].between(bbox[2], bbox[3])])

        if not frames:
            raise RuntimeError("No catalogue data found.")

        self.events_df = pd.concat(frames, ignore_index=True)
        self._postprocess_events()
        self._load_legend()
        self._build_colormap()
        self._load_faults()
        self._load_stations()

        self._loaded = True
        logger.info("Data loaded: %d events", len(self.events_df))

    # -----------------------------------------------------------------
    def _postprocess_events(self):
        self.events_df[self.mandatory_mag_col] = pd.to_numeric(
            self.events_df[self.mandatory_mag_col], errors="coerce"
        )
        self.events_df.dropna(subset=[self.mandatory_mag_col], inplace=True)

        if self.calculate_distance:
            calculate_distances_vectorized(
                self.events_df,
                self.mc.latitude,
                self.mc.longitude,
                out_col="Repi",
            )
            lim = self.mc.radius_km * (self.ec.event_radius_multiplier or 1.0)
            self.events_df = self.events_df[self.events_df["Repi"] <= lim]

        if self.ec.vmin is not None:
            self.events_df = self.events_df[
                self.events_df[self.mandatory_mag_col] >= self.ec.vmin
            ]
        if self.ec.vmax is not None:
            self.events_df = self.events_df[
                self.events_df[self.mandatory_mag_col] <= self.ec.vmax
            ]

    # -----------------------------------------------------------------
    def _load_legend(self):
        if self.legend_csv and self.legend_csv.exists():
            df = pd.read_csv(self.legend_csv)
            self.legend_map = {
                str(r["Field"]).strip(): str(r["Legend"]).strip()
                for _, r in df.iterrows()
            }
            logger.info("Legend loaded (%d entries).", len(self.legend_map))

    # -----------------------------------------------------------------
    def _build_colormap(self):
        import matplotlib.pyplot as plt

        mags = self.events_df[self.mandatory_mag_col]
        vmin = self.ec.vmin or math.floor(mags.min() * 2) / 2
        vmax = self.ec.vmax or math.ceil(mags.max() * 2) / 2
        cmap = plt.get_cmap(self.ec.color_palette)
        if self.ec.color_reversed:
            cmap = cmap.reversed()
        colors = [cmap(i / cmap.N) for i in range(cmap.N)]
        self.color_map = branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax)
        self.color_map.caption = self.ec.legend_title or "Magnitude"

    # -----------------------------------------------------------------
    def _load_faults(self):
        if not (self.fc and self.fc.include_faults):
            return
        try:
            self.faults_gdf = load_faults(
                self.fc.faults_gem_file_path, self.fc.coordinate_system
            )
        except Exception as e:
            logger.warning("Faults loading failed: %s", e)

    # -----------------------------------------------------------------
    def _load_stations(self):
        if not (self.sc and self.sc.station_file_path):
            return
        try:
            self.stations_df = load_stations_csv(
                self.sc.station_file_path, self.sc.coordinate_system
            )
        except Exception as e:
            logger.warning("Stations loading failed: %s", e)

    # -----------------------------------------------------------------
    def _add_tile_layers(self, m: folium.Map):
        """Add all tile layers, making the configured one default."""
        default = self.mc.default_tile_layer
        for name, cfg in TILE_LAYER_CONFIGS.items():
            folium.TileLayer(
                tiles=cfg["tiles"],
                attr=cfg["attr"],
                name=name,
                control=True,
                max_zoom=self.mc.max_zoom_level,
                min_zoom=self.mc.min_zoom_level,
                show=(name == default),
            ).add_to(m)

    # -----------------------------------------------------------------
    def _add_color_legend(self, m: folium.Map):
        if self.color_map:
            self.color_map.position = self.ec.legend_position.lower()
            self.color_map.add_to(m)
