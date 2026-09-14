"""Safe GeoTIFF inspection utilities for Everest Intelligence."""

from pathlib import Path
from typing import Any

import rasterio


def inspect_geotiff(file_path: str | Path) -> dict[str, Any]:
    """Inspect basic metadata from a GeoTIFF without modifying the file."""

    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"GeoTIFF file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Provided path is not a file: {path}")

    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError("Only .tif and .tiff files are supported.")

    with rasterio.open(path) as dataset:
        return {
            "file_name": path.name,
            "width": dataset.width,
            "height": dataset.height,
            "band_count": dataset.count,
            "crs": str(dataset.crs) if dataset.crs else None,
            "bounds": tuple(dataset.bounds),
            "transform": tuple(dataset.transform),
            "data_types": list(dataset.dtypes),
            "no_data_value": dataset.nodata,
        }