import tempfile
import unittest
from pathlib import Path

from src.everest_intelligence.satellite_scene import SatelliteScene


class TestSatelliteScene(unittest.TestCase):
    def create_fake_band(self, directory: str, filename: str) -> Path:
        file_path = Path(directory) / filename
        file_path.write_text("test band")
        return file_path

    def test_valid_scene_is_created(self):
        with tempfile.TemporaryDirectory() as directory:
            green_band = self.create_fake_band(directory, "green.tif")
            nir_band = self.create_fake_band(directory, "nir.tif")

            scene = SatelliteScene(
                green_band=green_band,
                nir_band=nir_band,
                scene_id="  Nepal-Water-Test-01  ",
            )

            self.assertEqual(scene.scene_id, "Nepal-Water-Test-01")
            self.assertEqual(scene.green_band, green_band.resolve())
            self.assertEqual(scene.nir_band, nir_band.resolve())

    def test_empty_scene_id_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_band = self.create_fake_band(directory, "green.tif")
            nir_band = self.create_fake_band(directory, "nir.tif")

            with self.assertRaises(ValueError):
                SatelliteScene(green_band, nir_band, "   ")

    def test_missing_green_band_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            nir_band = self.create_fake_band(directory, "nir.tif")

            with self.assertRaises(FileNotFoundError):
                SatelliteScene(
                    Path(directory) / "missing_green.tif",
                    nir_band,
                    "test-scene",
                )

    def test_missing_nir_band_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_band = self.create_fake_band(directory, "green.tif")

            with self.assertRaises(FileNotFoundError):
                SatelliteScene(
                    green_band,
                    Path(directory) / "missing_nir.tif",
                    "test-scene",
                )

    def test_invalid_green_extension_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_band = self.create_fake_band(directory, "green.txt")
            nir_band = self.create_fake_band(directory, "nir.tif")

            with self.assertRaises(ValueError):
                SatelliteScene(green_band, nir_band, "test-scene")

    def test_invalid_nir_extension_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            green_band = self.create_fake_band(directory, "green.tif")
            nir_band = self.create_fake_band(directory, "nir.txt")

            with self.assertRaises(ValueError):
                SatelliteScene(green_band, nir_band, "test-scene")


if __name__ == "__main__":
    unittest.main()
