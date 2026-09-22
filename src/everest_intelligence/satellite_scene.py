"""Validated representation of a local satellite scene."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.everest_intelligence.scene_metadata import SceneMetadata


@dataclass(frozen=True)
class SatelliteScene:
    """Validated Green/NIR satellite scene inputs and metadata."""

    green_band: Path
    nir_band: Path
    scene_id: str
    metadata: SceneMetadata | None = None

    def __post_init__(self) -> None:
        """Validate scene identity, files, and supported raster formats."""
        scene_id = self.scene_id.strip()
        if not scene_id:
            raise ValueError("Scene ID must not be empty.")
        object.__setattr__(self, "scene_id", scene_id)

        green = Path(self.green_band).expanduser().resolve()
        nir = Path(self.nir_band).expanduser().resolve()

        for band_name, band_path in (
            ("Green", green),
            ("NIR", nir),
        ):
            if not band_path.exists():
                raise FileNotFoundError(
                    f"{band_name} band does not exist: {band_path}"
                )

            if not band_path.is_file():
                raise ValueError(
                    f"{band_name} band is not a file: {band_path}"
                )

            if band_path.suffix.lower() not in {".tif", ".tiff"}:
                raise ValueError(
                    f"{band_name} band must be a GeoTIFF (.tif or .tiff): "
                    f"{band_path}"
                )

        object.__setattr__(self, "green_band", green)
        object.__setattr__(self, "nir_band", nir)
