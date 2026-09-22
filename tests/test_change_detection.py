"""Tests for temporal NDWI change detection."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.change_detection import detect_ndwi_change
from src.everest_intelligence.satellite_scene import SatelliteScene
from src.everest_intelligence.scene_metadata import SceneMetadata
from src.everest_intelligence.scene_pair import ScenePair


class TestChangeDetection(unittest.TestCase):
    def create_band(
        self,
        path: Path,
        data: np.ndarray,
    ) -> None:
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=from_origin(85.0, 28.0, 0.01, 0.01),
        ) as dataset:
            dataset.write(data.astype(np.float32), 1)

    def create_scene(
        self,
        directory: Path,
        scene_id: str,
        acquisition_datetime: datetime,
        green: np.ndarray,
        nir: np.ndarray,
    ) -> SatelliteScene:
        green_path = directory / f"{scene_id}_green.tif"
        nir_path = directory / f"{scene_id}_nir.tif"

        self.create_band(green_path, green)
        self.create_band(nir_path, nir)

        metadata = SceneMetadata(
            platform="Sentinel-2",
            sensor="MSI",
            acquisition_datetime=acquisition_datetime,
            processing_level="Level-2A",
            provider="Test Provider",
            resolution_m=10.0,
        )

        return SatelliteScene(
            scene_id=scene_id,
            green_band=green_path,
            nir_band=nir_path,
            metadata=metadata,
        )

    def create_pair(self, directory: Path) -> ScenePair:
        earlier_green = np.array(
            [[0.8, 0.8], [0.5, 0.5]],
            dtype=np.float32,
        )
        earlier_nir = np.array(
            [[0.2, 0.2], [0.5, 0.5]],
            dtype=np.float32,
        )

        later_green = np.array(
            [[0.9, 0.8], [0.4, 0.5]],
            dtype=np.float32,
        )
        later_nir = np.array(
            [[0.1, 0.2], [0.6, 0.5]],
            dtype=np.float32,
        )

        earlier = self.create_scene(
            directory,
            "scene-early",
            datetime(2026, 1, 1, 10, 0),
            earlier_green,
            earlier_nir,
        )

        later = self.create_scene(
            directory,
            "scene-late",
            datetime(2026, 1, 11, 10, 0),
            later_green,
            later_nir,
        )

        return ScenePair(earlier=earlier, later=later)

    def test_change_detection_returns_expected_pixel_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pair = self.create_pair(Path(temp_dir))

            result = detect_ndwi_change(
                pair,
                change_threshold=0.10,
            )

            self.assertEqual(result["total_pixels"], 4)
            self.assertEqual(
                result["increased_pixels"] + result["decreased_pixels"]
                + result["stable_pixels"],
                4,
            )

    def test_change_percentages_sum_to_one_hundred(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pair = self.create_pair(Path(temp_dir))

            result = detect_ndwi_change(
                pair,
                change_threshold=0.10,
            )

            total_percentage = (
                result["increased_percentage"]
                + result["decreased_percentage"]
                + result["stable_percentage"]
            )

            self.assertAlmostEqual(total_percentage, 100.0, places=4)

    def test_difference_array_has_expected_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pair = self.create_pair(Path(temp_dir))

            result = detect_ndwi_change(pair)

            self.assertEqual(result["ndwi_difference"].shape, (2, 2))

    def test_invalid_change_threshold_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pair = self.create_pair(Path(temp_dir))

            with self.assertRaises(ValueError):
                detect_ndwi_change(pair, change_threshold=0)

    def test_change_direction_is_measured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            pair = self.create_pair(Path(temp_dir))

            result = detect_ndwi_change(
                pair,
                change_threshold=0.10,
            )

            self.assertGreater(result["maximum_ndwi_increase"], 0)
            self.assertLess(result["maximum_ndwi_decrease"], 0)


if __name__ == "__main__":
    unittest.main()
