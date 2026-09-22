import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.satellite_scene import SatelliteScene
from src.everest_intelligence.scene_report import create_scene_report


class TestSceneReport(unittest.TestCase):
    def create_band(self, path: Path, data: np.ndarray) -> None:
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs="EPSG:4326",
            transform=from_origin(85.0, 28.0, 0.1, 0.1),
        ) as dataset:
            dataset.write(data, 1)

    def create_scene(self, directory: str) -> SatelliteScene:
        green_path = Path(directory) / "green.tif"
        nir_path = Path(directory) / "nir.tif"
        self.create_band(green_path, np.array([[0.6, 0.2], [0.2, 0.6]], dtype=np.float32))
        self.create_band(nir_path, np.array([[0.2, 0.6], [0.2, 0.2]], dtype=np.float32))
        return SatelliteScene(green_path, nir_path, "nepal-water-01")

    def test_report_contains_analysis_and_spatial_context(self):
        with tempfile.TemporaryDirectory() as directory:
            report = create_scene_report(self.create_scene(directory))

        self.assertEqual(report["scene_id"], "nepal-water-01")
        self.assertEqual(report["input_bands"], {"green": "green.tif", "nir": "nir.tif"})
        self.assertEqual(report["analysis"]["index"], "NDWI")
        self.assertEqual(report["analysis"]["total_pixels"], 4)
        self.assertEqual(report["analysis"]["detected_water_pixels"], 2)
        self.assertEqual(report["analysis"]["detected_water_percentage"], 50.0)
        self.assertEqual(report["spatial_metadata"]["crs"], "EPSG:4326")
        self.assertEqual(report["spatial_metadata"]["bounds"], {
            "west": 85.0, "south": 27.8, "east": 85.2, "north": 28.0,
        })
        self.assertEqual(report["spatial_metadata"]["pixel_size"], {"x": 0.1, "y": 0.1})

    def test_report_is_json_serializable_and_excludes_raster_arrays(self):
        with tempfile.TemporaryDirectory() as directory:
            report = create_scene_report(self.create_scene(directory), threshold=0.4)

        serialized = json.dumps(report)

        self.assertIn('"threshold": 0.4', serialized)
        self.assertNotIn("water_mask", report)
        self.assertNotIn("ndwi", report)

    def test_invalid_threshold_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                create_scene_report(self.create_scene(directory), threshold=1.1)


if __name__ == "__main__":
    unittest.main()


class TestSceneReportMetadata(TestSceneReport):
    def test_scene_metadata_is_included_in_report(self):
        from datetime import datetime, timezone

        from src.everest_intelligence.scene_metadata import SceneMetadata

        with tempfile.TemporaryDirectory() as directory:
            green_path = Path(directory) / "green.tif"
            nir_path = Path(directory) / "nir.tif"

            self.create_band(
                green_path,
                np.array([[0.6]], dtype=np.float32),
            )
            self.create_band(
                nir_path,
                np.array([[0.2]], dtype=np.float32),
            )

            metadata = SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=datetime(
                    2026,
                    9,
                    22,
                    10,
                    30,
                    tzinfo=timezone.utc,
                ),
                processing_level="L2A",
                provider="Copernicus Data Space",
                resolution_m=10.0,
                cloud_cover_percent=12.5,
                source_uri="https://example.test/scene-01",
            )

            scene = SatelliteScene(
                green_band=green_path,
                nir_band=nir_path,
                scene_id="metadata-report-01",
                metadata=metadata,
            )

            report = create_scene_report(scene)

            self.assertIn("scene_metadata", report)
            self.assertEqual(
                report["scene_metadata"]["platform"],
                "Sentinel-2",
            )
            self.assertEqual(
                report["scene_metadata"]["sensor"],
                "MSI",
            )
            self.assertEqual(
                report["scene_metadata"]["resolution_m"],
                10.0,
            )
            self.assertEqual(
                report["scene_metadata"]["cloud_cover_percent"],
                12.5,
            )
            self.assertEqual(
                report["scene_metadata"]["acquisition_datetime"],
                "2026-09-22T10:30:00+00:00",
            )

    def test_report_without_metadata_remains_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            green_path = Path(directory) / "green.tif"
            nir_path = Path(directory) / "nir.tif"

            self.create_band(
                green_path,
                np.array([[0.6]], dtype=np.float32),
            )
            self.create_band(
                nir_path,
                np.array([[0.2]], dtype=np.float32),
            )

            scene = SatelliteScene(
                green_band=green_path,
                nir_band=nir_path,
                scene_id="no-metadata-01",
            )

            report = create_scene_report(scene)

            self.assertNotIn("scene_metadata", report)
