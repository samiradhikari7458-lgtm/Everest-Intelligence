"""Validated temporal pairing of Earth-observation scenes."""

from __future__ import annotations

from dataclasses import dataclass

from src.everest_intelligence.raster_loader import load_scene_bands
from src.everest_intelligence.satellite_scene import SatelliteScene


@dataclass(frozen=True)
class ScenePair:
    """Represent two spatially comparable scenes in chronological order."""

    earlier: SatelliteScene
    later: SatelliteScene

    def __post_init__(self) -> None:
        if self.earlier.scene_id == self.later.scene_id:
            raise ValueError("Scene pair must contain two different scenes.")

        if self.earlier.metadata is None:
            raise ValueError("Earlier scene must have metadata.")

        if self.later.metadata is None:
            raise ValueError("Later scene must have metadata.")

        if (
            self.earlier.metadata.acquisition_datetime
            >= self.later.metadata.acquisition_datetime
        ):
            raise ValueError(
                "Earlier scene must have an acquisition time before the later scene."
            )

        earlier_bands = load_scene_bands(self.earlier)
        later_bands = load_scene_bands(self.later)

        if earlier_bands["green"].shape != later_bands["green"].shape:
            raise ValueError(
                "Scene pair must have matching raster dimensions."
            )

        if earlier_bands["crs"] != later_bands["crs"]:
            raise ValueError(
                "Scene pair must use the same coordinate reference system."
            )

        if earlier_bands["transform"] != later_bands["transform"]:
            raise ValueError(
                "Scene pair must use the same spatial transform."
            )
