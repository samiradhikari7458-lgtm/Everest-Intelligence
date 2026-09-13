from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def calculate_ndwi(green_band, nir_band):
    """
    Calculate the Normalized Difference Water Index.
    """
    denominator = green_band + nir_band + 1e-10
    return (green_band - nir_band) / denominator


def create_synthetic_bands(height=200, width=300):
    """
    Create simulated Green and Near-Infrared satellite bands.
    """
    rng = np.random.default_rng(42)

    green_band = rng.uniform(
        0.1,
        0.8,
        size=(height, width),
    )

    nir_band = rng.uniform(
        0.2,
        0.9,
        size=(height, width),
    )

    # Simulate a water region.
    green_band[60:140, 90:220] = rng.uniform(
        0.55,
        0.8,
        size=(80, 130),
    )

    nir_band[60:140, 90:220] = rng.uniform(
        0.05,
        0.25,
        size=(80, 130),
    )

    return green_band, nir_band


def save_ndwi_visualization(ndwi, water_mask):
    """
    Save the NDWI and detected water images.
    """
    project_root = Path(__file__).resolve().parent.parent
    output_directory = project_root / "data" / "processed"

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_directory / "ndwi_demo.png"

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5),
    )

    axes[0].imshow(ndwi, cmap="BrBG")
    axes[0].set_title("NDWI Image")
    axes[0].axis("off")

    axes[1].imshow(water_mask, cmap="Blues")
    axes[1].set_title("Detected Water Area")
    axes[1].axis("off")

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_path


def main():
    """
    Run the NDWI water-detection demonstration.
    """
    green_band, nir_band = create_synthetic_bands()

    ndwi = calculate_ndwi(
        green_band,
        nir_band,
    )

    water_mask = ndwi > 0.2

    output_path = save_ndwi_visualization(
        ndwi,
        water_mask,
    )

    print("NDWI water-detection prototype completed.")
    print(f"Detected water pixels: {water_mask.sum()}")
    print(f"Output image saved to: {output_path}")


if __name__ == "__main__":
    main()
