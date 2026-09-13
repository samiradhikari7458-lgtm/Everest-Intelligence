from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "processed"

NDWI_THRESHOLD = 0.20
RANDOM_SEED = 42


def calculate_ndwi(
    green_band: np.ndarray,
    nir_band: np.ndarray,
) -> np.ndarray:
    """
    Calculate the Normalized Difference Water Index.

    NDWI = (Green - NIR) / (Green + NIR)

    Parameters
    ----------
    green_band:
        Green-band reflectance values.

    nir_band:
        Near-infrared reflectance values.

    Returns
    -------
    np.ndarray
        NDWI values.

    Raises
    ------
    ValueError
        If the input arrays have different shapes or contain invalid values.
    """
    if green_band.shape != nir_band.shape:
        raise ValueError("Green and NIR bands must have the same shape.")

    if not np.all(np.isfinite(green_band)):
        raise ValueError("Green band contains invalid values.")

    if not np.all(np.isfinite(nir_band)):
        raise ValueError("NIR band contains invalid values.")

    denominator = green_band + nir_band

    with np.errstate(divide="ignore", invalid="ignore"):
        ndwi = np.divide(
            green_band - nir_band,
            denominator,
            out=np.zeros_like(green_band, dtype=np.float64),
            where=denominator != 0,
        )

    return ndwi


def create_synthetic_bands(
    height: int = 300,
    width: int = 400,
    seed: int = RANDOM_SEED,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Create reproducible synthetic green and NIR satellite bands.

    The central rectangle represents a simplified water-like area.
    This is for software testing only, not real satellite analysis.
    """
    if height <= 0 or width <= 0:
        raise ValueError("Image height and width must be positive.")

    rng = np.random.default_rng(seed)

    green_band = rng.uniform(
        low=0.20,
        high=0.45,
        size=(height, width),
    )

    nir_band = rng.uniform(
        low=0.35,
        high=0.60,
        size=(height, width),
    )

    water_top = height // 3
    water_bottom = (height * 2) // 3
    water_left = width // 3
    water_right = (width * 2) // 3

    green_band[water_top:water_bottom, water_left:water_right] = rng.uniform(
        low=0.45,
        high=0.65,
        size=(water_bottom - water_top, water_right - water_left),
    )

    nir_band[water_top:water_bottom, water_left:water_right] = rng.uniform(
        low=0.05,
        high=0.20,
        size=(water_bottom - water_top, water_right - water_left),
    )

    return green_band, nir_band


def create_report(
    ndwi: np.ndarray,
    water_mask: np.ndarray,
    threshold: float,
) -> dict[str, object]:
    """
    Create a structured scientific summary of the detection result.
    """
    total_pixels = int(ndwi.size)
    detected_water_pixels = int(np.count_nonzero(water_mask))
    water_percentage = (detected_water_pixels / total_pixels) * 100

    return {
        "software": "Everest Intelligence",
        "module": "NDWI Water Detection Prototype",
        "input_type": "Synthetic demonstration",
        "scientific_status": "Experimental - not validated with real satellite data",
        "image_height_pixels": int(ndwi.shape[0]),
        "image_width_pixels": int(ndwi.shape[1]),
        "total_pixels": total_pixels,
        "ndwi_threshold": threshold,
        "ndwi_minimum": float(np.min(ndwi)),
        "ndwi_maximum": float(np.max(ndwi)),
        "ndwi_average": float(np.mean(ndwi)),
        "detected_water_pixels": detected_water_pixels,
        "detected_water_percentage": round(water_percentage, 4),
        "random_seed": RANDOM_SEED,
    }


def save_visualization(
    ndwi: np.ndarray,
    water_mask: np.ndarray,
    output_path: Path,
) -> None:
    """
    Save the NDWI image and detected-water mask.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axes = plt.subplots(1, 2, figsize=(14, 6))

    ndwi_image = axes[0].imshow(ndwi, cmap="BrBG", vmin=-1, vmax=1)
    axes[0].set_title("NDWI Image")
    axes[0].set_xlabel("Pixel column")
    axes[0].set_ylabel("Pixel row")
    figure.colorbar(ndwi_image, ax=axes[0], fraction=0.046, pad=0.04)

    water_image = axes[1].imshow(water_mask, cmap="Blues", vmin=0, vmax=1)
    axes[1].set_title("Detected Water Area")
    axes[1].set_xlabel("Pixel column")
    axes[1].set_ylabel("Pixel row")
    figure.colorbar(water_image, ax=axes[1], fraction=0.046, pad=0.04)

    figure.suptitle(
        "Everest Intelligence - NDWI Water Detection",
        fontsize=16,
    )

    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_report(report: dict[str, object], output_path: Path) -> None:
    """
    Save the detection report as formatted JSON.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=4)


def main() -> None:
    """
    Execute the complete NDWI demonstration pipeline.
    """
    output_image_path = OUTPUT_DIRECTORY / "ndwi_demo.png"
    output_report_path = OUTPUT_DIRECTORY / "ndwi_report.json"

    green_band, nir_band = create_synthetic_bands()
    ndwi = calculate_ndwi(green_band, nir_band)
    water_mask = ndwi > NDWI_THRESHOLD

    report = create_report(
        ndwi=ndwi,
        water_mask=water_mask,
        threshold=NDWI_THRESHOLD,
    )

    save_visualization(
        ndwi=ndwi,
        water_mask=water_mask,
        output_path=output_image_path,
    )

    save_report(
        report=report,
        output_path=output_report_path,
    )

    print("Everest Intelligence NDWI pipeline completed.")
    print(f"Detected water pixels: {report['detected_water_pixels']}")
    print(f"Detected water percentage: {report['detected_water_percentage']}%")
    print(f"NDWI threshold: {NDWI_THRESHOLD}")
    print(f"Image saved to: {output_image_path}")
    print(f"Report saved to: {output_report_path}")


if __name__ == "__main__":
    main()
