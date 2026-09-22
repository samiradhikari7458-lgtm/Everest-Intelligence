"""Validated NDWI analysis for Everest Intelligence."""

from typing import Any

import numpy as np

from src.ndwi_demo import calculate_ndwi
from src.everest_intelligence.raster_loader import load_scene_bands
from src.everest_intelligence.satellite_scene import SatelliteScene


def analyze_scene(
    scene: SatelliteScene,
    threshold: float = 0.20,
) -> dict[str, Any]:
    """Load a validated satellite scene and calculate NDWI water detection."""

    if not -1.0 <= threshold <= 1.0:
        raise ValueError("NDWI threshold must be between -1.0 and 1.0.")

    bands = load_scene_bands(scene)

    ndwi = calculate_ndwi(
        green_band=bands["green"],
        nir_band=bands["nir"],
    )

    water_mask = ndwi > threshold

    return {
        "scene_id": bands["scene_id"],
        "ndwi": ndwi,
        "water_mask": water_mask,
        "threshold": threshold,
        "total_pixels": int(ndwi.size),
        "detected_water_pixels": int(np.count_nonzero(water_mask)),
        "detected_water_percentage": round(
            float(np.count_nonzero(water_mask) / ndwi.size * 100),
            4,
        ),
        "crs": bands["crs"],
        "transform": bands["transform"],
        "profile": bands["profile"],
    }
