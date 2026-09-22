"""Temporal NDWI change detection for validated satellite scene pairs."""

from __future__ import annotations

from typing import Any

import numpy as np

from src.everest_intelligence.ndwi_analysis import analyze_scene
from src.everest_intelligence.scene_pair import ScenePair


def detect_ndwi_change(
    scene_pair: ScenePair,
    change_threshold: float = 0.10,
) -> dict[str, Any]:
    """Compare NDWI between two spatially aligned satellite scenes."""
    if change_threshold <= 0:
        raise ValueError("Change threshold must be greater than zero.")

    earlier_analysis = analyze_scene(scene_pair.earlier)
    later_analysis = analyze_scene(scene_pair.later)

    earlier_ndwi = earlier_analysis["ndwi"]
    later_ndwi = later_analysis["ndwi"]

    if earlier_ndwi.shape != later_ndwi.shape:
        raise ValueError("NDWI arrays must have matching dimensions.")

    difference = later_ndwi - earlier_ndwi

    increase_mask = difference >= change_threshold
    decrease_mask = difference <= -change_threshold
    stable_mask = ~(increase_mask | decrease_mask)

    total_pixels = int(difference.size)

    return {
        "earlier_scene_id": scene_pair.earlier.scene_id,
        "later_scene_id": scene_pair.later.scene_id,
        "change_threshold": change_threshold,
        "total_pixels": total_pixels,
        "increased_pixels": int(np.count_nonzero(increase_mask)),
        "decreased_pixels": int(np.count_nonzero(decrease_mask)),
        "stable_pixels": int(np.count_nonzero(stable_mask)),
        "increased_percentage": round(
            float(np.count_nonzero(increase_mask) / total_pixels * 100),
            4,
        ),
        "decreased_percentage": round(
            float(np.count_nonzero(decrease_mask) / total_pixels * 100),
            4,
        ),
        "stable_percentage": round(
            float(np.count_nonzero(stable_mask) / total_pixels * 100),
            4,
        ),
        "mean_ndwi_change": float(np.mean(difference)),
        "maximum_ndwi_increase": float(np.max(difference)),
        "maximum_ndwi_decrease": float(np.min(difference)),
        "ndwi_difference": difference,
    }
