"""Portable summaries of offline satellite-scene analyses."""

from __future__ import annotations

from typing import Any

from rasterio.transform import array_bounds

from src.everest_intelligence.ndwi_analysis import analyze_scene
from src.everest_intelligence.satellite_scene import SatelliteScene


def create_scene_report(
    scene: SatelliteScene,
    threshold: float = 0.20,
) -> dict[str, Any]:
    """Analyze a local scene and return a JSON-ready NDWI summary.

    The report deliberately omits the full NDWI array and water mask.  That
    keeps it small, portable, and safe to save or share while preserving the
    measurements and spatial context needed to interpret a detection result.
    """

    analysis = analyze_scene(scene, threshold=threshold)
    profile = analysis["profile"]
    transform = analysis["transform"]
    height = int(profile["height"])
    width = int(profile["width"])
    west, south, east, north = array_bounds(height, width, transform)
    crs = analysis["crs"]

    return {
        "scene_id": analysis["scene_id"],
        "input_bands": {
            "green": scene.green_band.name,
            "nir": scene.nir_band.name,
        },
        "analysis": {
            "index": "NDWI",
            "threshold": analysis["threshold"],
            "total_pixels": analysis["total_pixels"],
            "detected_water_pixels": analysis["detected_water_pixels"],
            "detected_water_percentage": analysis["detected_water_percentage"],
        },
        "spatial_metadata": {
            "width": width,
            "height": height,
            "crs": crs.to_string() if crs else None,
            "bounds": {
                "west": float(west),
                "south": float(south),
                "east": float(east),
                "north": float(north),
            },
            "pixel_size": {
                "x": float(transform.a),
                "y": abs(float(transform.e)),
            },
        },
    }
