"""Validated satellite scene structure for Everest Intelligence."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SatelliteScene:
    """Describe the required bands for a satellite scene."""

    green_band: Path
    nir_band: Path
    scene_id: str

    def __post_init__(self) -> None:
        green = Path(self.green_band).expanduser().resolve()
        nir = Path(self.nir_band).expanduser().resolve()

        if not self.scene_id.strip():
            raise ValueError("scene_id cannot be empty.")

        if green.suffix.lower() not in {".tif", ".tiff"}:
            raise ValueError("green_band must be a GeoTIFF file.")

        if nir.suffix.lower() not in {".tif", ".tiff"}:
            raise ValueError("nir_band must be a GeoTIFF file.")

        if not green.exists():
            raise FileNotFoundError(f"Green band not found: {green}")

        if not nir.exists():
            raise FileNotFoundError(f"NIR band not found: {nir}")

        object.__setattr__(self, "green_band", green)
        object.__setattr__(self, "nir_band", nir)
        object.__setattr__(self, "scene_id", self.scene_id.strip())
