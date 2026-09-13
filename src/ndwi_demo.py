import numpy as np
import matplotlib.pyplot as plt


def calculate_ndwi(green_band, nir_band):
    """
    Calculate the Normalized Difference Water Index.
    """
    return (green_band - nir_band) / (
        green_band + nir_band + 1e-10
    )


# Create a reproducible synthetic satellite-like image
rng = np.random.default_rng(42)

height = 200
width = 300

green_band = rng.uniform(0.1, 0.8, size=(height, width))
nir_band = rng.uniform(0.2, 0.9, size=(height, width))

# Create an artificial water region
green_band[60:140, 90:220] = rng.uniform(
    0.55, 0.8, size=(80, 130)
)

nir_band[60:140, 90:220] = rng.uniform(
    0.05, 0.25, size=(80, 130)
)

# Calculate NDWI
ndwi = calculate_ndwi(green_band, nir_band)

# Classify pixels as water or non-water
water_mask = ndwi > 0.2

# Display results
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].imshow(ndwi, cmap="BrBG")
axes[0].set_title("NDWI Image")
axes[0].axis("off")

axes[1].imshow(water_mask, cmap="Blues")
axes[1].set_title("Detected Water Area")
axes[1].axis("off")

plt.tight_layout()

output_path = "data/processed/ndwi_demo.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")

print("NDWI water-detection prototype completed.")
print(f"Detected water pixels: {water_mask.sum()}")
print(f"Output image saved to: {output_path}")
