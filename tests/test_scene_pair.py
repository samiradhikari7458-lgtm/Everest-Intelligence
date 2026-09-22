"""Tests for temporal scene pairing."""

import tempfile
import unittest

import numpy as np
from datetime import datetime
from pathlib import Path

import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.satellite_scene import SatelliteScene
from src.everest_intelligence.scene_metadata import SceneMetadata
from src.everest_intelligence.scene_pair import ScenePair


class TestScenePair(unittest.TestCase):
    def create_band(self, path: Path) -> None:
        data = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)

        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=2,
            width=2,
            count=1,
            dtype="float32",
            crs="EPSG:4326",
            transform=from_origin(85.0, 28.0, 0.01, 0.01),
        ) as dataset:
            dataset.write(data, 1)

    def create_scene(
        self,
        directory: Path,
        scene_id: str,
        acquisition_datetime: datetime,
    ) -> SatelliteScene:
        green = directory / f"{scene_id}_green.tif"
        nir = directory / f"{scene_id}_nir.tif"

        self.create_band(green)
        self.create_band(nir)

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
            green_band=green,
            nir_band=nir,
            metadata=metadata,
        )

    def test_chronological_pair_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 1, 1, 10, 0),
            )
            later = self.create_scene(
                directory,
                "scene-late",
                datetime(2026, 1, 11, 10, 0),
            )

            pair = ScenePair(earlier=earlier, later=later)

            self.assertEqual(pair.earlier.scene_id, "scene-early")
            self.assertEqual(pair.later.scene_id, "scene-late")

    def test_same_scene_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            scene = self.create_scene(
                directory,
                "same-scene",
                datetime(2026, 1, 1, 10, 0),
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=scene, later=scene)

    def test_missing_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 1, 1, 10, 0),
            )

            later_green = directory / "scene-late_green.tif"
            later_nir = directory / "scene-late_nir.tif"
            self.create_band(later_green)
            self.create_band(later_nir)

            later = SatelliteScene(
                scene_id="scene-late",
                green_band=later_green,
                nir_band=later_nir,
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=earlier, later=later)

    def test_reverse_chronology_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 2, 1, 10, 0),
            )
            later = self.create_scene(
                directory,
                "scene-late",
                datetime(2026, 1, 1, 10, 0),
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=earlier, later=later)

    def test_different_dimensions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 1, 1, 10, 0),
            )

            green = directory / "scene-late_green.tif"
            nir = directory / "scene-late_nir.tif"

            data = np.ones((3, 2), dtype=np.float32)

            for path in (green, nir):
                with rasterio.open(
                    path,
                    "w",
                    driver="GTiff",
                    height=3,
                    width=2,
                    count=1,
                    dtype="float32",
                    crs="EPSG:4326",
                    transform=from_origin(85.0, 28.0, 0.01, 0.01),
                ) as dataset:
                    dataset.write(data, 1)

            metadata = SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=datetime(2026, 1, 11, 10, 0),
                processing_level="Level-2A",
                provider="Test Provider",
                resolution_m=10.0,
            )

            later = SatelliteScene(
                scene_id="scene-late",
                green_band=green,
                nir_band=nir,
                metadata=metadata,
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=earlier, later=later)

    def test_different_crs_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 1, 1, 10, 0),
            )

            green = directory / "scene-late_green.tif"
            nir = directory / "scene-late_nir.tif"

            data = np.ones((2, 2), dtype=np.float32)

            for path in (green, nir):
                with rasterio.open(
                    path,
                    "w",
                    driver="GTiff",
                    height=2,
                    width=2,
                    count=1,
                    dtype="float32",
                    crs="EPSG:3857",
                    transform=from_origin(85.0, 28.0, 0.01, 0.01),
                ) as dataset:
                    dataset.write(data, 1)

            metadata = SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=datetime(2026, 1, 11, 10, 0),
                processing_level="Level-2A",
                provider="Test Provider",
                resolution_m=10.0,
            )

            later = SatelliteScene(
                scene_id="scene-late",
                green_band=green,
                nir_band=nir,
                metadata=metadata,
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=earlier, later=later)

    def test_different_spatial_transform_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)

            earlier = self.create_scene(
                directory,
                "scene-early",
                datetime(2026, 1, 1, 10, 0),
            )

            green = directory / "scene-late_green.tif"
            nir = directory / "scene-late_nir.tif"

            data = np.ones((2, 2), dtype=np.float32)

            for path in (green, nir):
                with rasterio.open(
                    path,
                    "w",
                    driver="GTiff",
                    height=2,
                    width=2,
                    count=1,
                    dtype="float32",
                    crs="EPSG:4326",
                    transform=from_origin(85.1, 28.0, 0.01, 0.01),
                ) as dataset:
                    dataset.write(data, 1)

            metadata = SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=datetime(2026, 1, 11, 10, 0),
                processing_level="Level-2A",
                provider="Test Provider",
                resolution_m=10.0,
            )

            later = SatelliteScene(
                scene_id="scene-late",
                green_band=green,
                nir_band=nir,
                metadata=metadata,
            )

            with self.assertRaises(ValueError):
                ScenePair(earlier=earlier, later=later)


if __name__ == "__main__":
    unittest.main()
