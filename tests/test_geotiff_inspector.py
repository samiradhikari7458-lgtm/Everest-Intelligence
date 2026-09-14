import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.geotiff_inspector import inspect_geotiff


class TestGeoTIFFInspector(unittest.TestCase):
    def create_test_geotiff(self, file_path: Path) -> None:
        data = np.array(
            [
                [1, 2, 3],
                [4, 5, 6],
            ],
            dtype=np.float32,
        )

        transform = from_origin(85.0, 28.0, 0.1, 0.1)

        with rasterio.open(
            file_path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs="EPSG:4326",
            transform=transform,
            nodata=-9999,
        ) as dataset:
            dataset.write(data, 1)

    def test_inspect_geotiff_returns_metadata(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "test_scene.tif"
            self.create_test_geotiff(file_path)

            metadata = inspect_geotiff(file_path)

            self.assertEqual(metadata["file_name"], "test_scene.tif")
            self.assertEqual(metadata["width"], 3)
            self.assertEqual(metadata["height"], 2)
            self.assertEqual(metadata["band_count"], 1)
            self.assertEqual(metadata["crs"], "EPSG:4326")
            self.assertEqual(metadata["data_types"], ["float32"])
            self.assertEqual(metadata["no_data_value"], -9999.0)

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            inspect_geotiff("/tmp/file_that_does_not_exist.tif")

    def test_invalid_extension_raises_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "not_a_geotiff.txt"
            file_path.write_text("test")

            with self.assertRaises(ValueError):
                inspect_geotiff(file_path)


if __name__ == "__main__":
    unittest.main()
