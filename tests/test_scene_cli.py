import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.everest_intelligence.scene_cli import main


class TestSceneCli(unittest.TestCase):
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

    def test_cli_prints_json_report_for_local_bands(self):
        with tempfile.TemporaryDirectory() as directory:
            green_path = Path(directory) / "green.tif"
            nir_path = Path(directory) / "nir.tif"
            self.create_band(green_path, np.array([[0.6]], dtype=np.float32))
            self.create_band(nir_path, np.array([[0.2]], dtype=np.float32))
            output = io.StringIO()

            with redirect_stdout(output):
                status = main([
                    "--green", str(green_path),
                    "--nir", str(nir_path),
                    "--scene-id", "local-test-01",
                    "--threshold", "0.3",
                ])

        report = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(report["scene_id"], "local-test-01")
        self.assertEqual(report["analysis"]["threshold"], 0.3)
        self.assertEqual(report["analysis"]["detected_water_pixels"], 1)

    def test_cli_rejects_invalid_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            green_path = Path(directory) / "green.tif"
            nir_path = Path(directory) / "nir.tif"
            data = np.array([[0.6]], dtype=np.float32)
            self.create_band(green_path, data)
            self.create_band(nir_path, data)

            with self.assertRaises(SystemExit) as raised:
                main([
                    "--green", str(green_path),
                    "--nir", str(nir_path),
                    "--scene-id", "local-test-01",
                    "--threshold", "1.1",
                ])

        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
