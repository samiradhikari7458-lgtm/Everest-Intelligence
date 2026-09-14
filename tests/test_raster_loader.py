import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.raster_loader import load_scene_bands
from src.everest_intelligence.satellite_scene import SatelliteScene


class TestRasterLoader(unittest.TestCase):
    def create_band(
        self,
        file_path: Path,
        data: np.ndarray,
        crs: str = "EPSG:4326",
        transform=None,
    ) -> None:
        if transform is None:
            transform = from_origin(85.0, 28.0, 0.1, 0.1)

        with rasterio.open(
            file_path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs=crs,
            transform=transform,
        ) as dataset:
            dataset.write(data, 1)

    def create_scene(
        self,
        directory: str,
        green_data: np.ndarray,
        nir_data: np.ndarray,
        green_crs: str = "EPSG:4326",
        nir_crs: str = "EPSG:4326",
        green_transform=None,
        nir_transform=None,
    ) -> SatelliteScene:
        directory_path = Path(directory)
        green_path = directory_path / "green.tif"
        nir_path = directory_path / "nir.tif"

        self.create_band(
            green_path,
            green_data,
            crs=green_crs,
            transform=green_transform,
        )
        self.create_band(
            nir_path,
            nir_data,
            crs=nir_crs,
            transform=nir_transform,
        )

        return SatelliteScene(
            green_band=green_path,
            nir_band=nir_path,
            scene_id="test-scene",
        )

    def test_matching_bands_are_loaded(self):
        with tempfile.TemporaryDirectory() as directory:
            green_data = np.array(
                [[1.0, 2.0], [3.0, 4.0]],
                dtype=np.float32,
            )
            nir_data = np.array(
                [[5.0, 6.0], [7.0, 8.0]],
                dtype=np.float32,
            )

            scene = self.create_scene(directory, green_data, nir_data)
            result = load_scene_bands(scene)

            np.testing.assert_array_equal(result["green"], green_data)
            np.testing.assert_array_equal(result["nir"], nir_data)
            self.assertEqual(result["scene_id"], "test-scene")
            self.assertEqual(result["crs"].to_string(), "EPSG:4326")

    def test_different_dimensions_raise_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_data = np.ones((2, 2), dtype=np.float32)
            nir_data = np.ones((3, 2), dtype=np.float32)

            scene = self.create_scene(directory, green_data, nir_data)

            with self.assertRaises(ValueError):
                load_scene_bands(scene)

    def test_different_crs_raise_error(self):
        with tempfile.TemporaryDirectory() as directory:
            data = np.ones((2, 2), dtype=np.float32)

            scene = self.create_scene(
                directory,
                data,
                data,
                green_crs="EPSG:4326",
                nir_crs="EPSG:3857",
            )

            with self.assertRaises(ValueError):
                load_scene_bands(scene)

    def test_different_transforms_raise_error(self):
        with tempfile.TemporaryDirectory() as directory:
            data = np.ones((2, 2), dtype=np.float32)

            green_transform = from_origin(85.0, 28.0, 0.1, 0.1)
            nir_transform = from_origin(86.0, 28.0, 0.1, 0.1)

            scene = self.create_scene(
                directory,
                data,
                data,
                green_transform=green_transform,
                nir_transform=nir_transform,
            )

            with self.assertRaises(ValueError):
                load_scene_bands(scene)

    def test_nan_values_raise_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_data = np.array(
                [[1.0, np.nan], [3.0, 4.0]],
                dtype=np.float32,
            )
            nir_data = np.ones((2, 2), dtype=np.float32)

            scene = self.create_scene(directory, green_data, nir_data)

            with self.assertRaises(ValueError):
                load_scene_bands(scene)

    def test_infinite_values_raise_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_data = np.ones((2, 2), dtype=np.float32)
            nir_data = np.array(
                [[1.0, 2.0], [np.inf, 4.0]],
                dtype=np.float32,
            )

            scene = self.create_scene(directory, green_data, nir_data)

            with self.assertRaises(ValueError):
                load_scene_bands(scene)


if __name__ == "__main__":
    unittest.main()
