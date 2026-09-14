"""Safe raster loading utilities for Everest Intelligence."""

from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from src.everest_intelligence.satellite_scene import SatelliteScene


def load_scene_bands(scene: SatelliteScene) -> dict[str, Any]:
    """Load and validate Green and NIR raster bands."""

    with rasterio.open(scene.green_band) as green_dataset:
        green_data = green_dataset.read(1)
        green_profile = green_dataset.profile.copy()
        green_crs = green_dataset.crs
        green_transform = green_dataset.transform

    with rasterio.open(scene.nir_band) as nir_dataset:
        nir_data = nir_dataset.read(1)
        nir_crs = nir_dataset.crs
        nir_transform = nir_dataset.transform

    if green_data.shape != nir_data.shape:
        raise ValueError("Green and NIR bands must have matching dimensions.")

    if green_crs != nir_crs:
        raise ValueError("Green and NIR bands must use the same CRS.")

    if green_transform != nir_transform:
        raise ValueError("Green and NIR bands must use the same spatial transform.")

    if not np.isfinite(green_data).all():
        raise ValueError("Green band contains invalid numeric values.")

    if not np.isfinite(nir_data).all():
        raise ValueError("NIR band contains invalid numeric values.")

    return {
        "scene_id": scene.scene_id,
        "green": green_data,
        "nir": nir_data,
        "profile": green_profile,
        "crs": green_crs,
        "transform": green_transform,
    }
