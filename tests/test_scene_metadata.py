import unittest
from datetime import datetime, timezone

from src.everest_intelligence.scene_metadata import SceneMetadata


class TestSceneMetadata(unittest.TestCase):
    def setUp(self):
        self.acquisition_datetime = datetime(
            2026,
            9,
            22,
            10,
            30,
            tzinfo=timezone.utc,
        )

    def test_valid_metadata(self):
        metadata = SceneMetadata(
            platform="Sentinel-2",
            sensor="MSI",
            acquisition_datetime=self.acquisition_datetime,
            processing_level="L2A",
            provider="Copernicus Data Space",
            resolution_m=10.0,
            cloud_cover_percent=12.5,
            source_uri="https://example.test/scene-01",
        )

        self.assertEqual(metadata.platform, "Sentinel-2")
        self.assertEqual(metadata.sensor, "MSI")
        self.assertEqual(metadata.resolution_m, 10.0)

    def test_metadata_serializes_to_json_compatible_dictionary(self):
        metadata = SceneMetadata(
            platform="Sentinel-2",
            sensor="MSI",
            acquisition_datetime=self.acquisition_datetime,
            processing_level="L2A",
            provider="Copernicus Data Space",
            resolution_m=10.0,
        )

        result = metadata.to_dict()

        self.assertEqual(result["platform"], "Sentinel-2")
        self.assertEqual(result["acquisition_datetime"], "2026-09-22T10:30:00+00:00")
        self.assertIsNone(result["cloud_cover_percent"])

    def test_empty_platform_rejected(self):
        with self.assertRaises(ValueError):
            SceneMetadata(
                platform="",
                sensor="MSI",
                acquisition_datetime=self.acquisition_datetime,
                processing_level="L2A",
                provider="Provider",
                resolution_m=10.0,
            )

    def test_invalid_resolution_rejected(self):
        with self.assertRaises(ValueError):
            SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=self.acquisition_datetime,
                processing_level="L2A",
                provider="Provider",
                resolution_m=0,
            )

    def test_invalid_cloud_cover_rejected(self):
        with self.assertRaises(ValueError):
            SceneMetadata(
                platform="Sentinel-2",
                sensor="MSI",
                acquisition_datetime=self.acquisition_datetime,
                processing_level="L2A",
                provider="Provider",
                resolution_m=10.0,
                cloud_cover_percent=101.0,
            )


if __name__ == "__main__":
    unittest.main()
