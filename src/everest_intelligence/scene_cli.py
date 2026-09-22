"""Command-line interface for creating a local satellite-scene report."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from rasterio.errors import RasterioError

from src.everest_intelligence.satellite_scene import SatelliteScene
from src.everest_intelligence.scene_report import create_scene_report


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for a local NDWI scene report."""

    parser = argparse.ArgumentParser(
        prog="everest-scene-report",
        description="Create a JSON NDWI report from local Green and NIR GeoTIFF bands.",
    )
    parser.add_argument("--green", required=True, help="Path to the Green-band GeoTIFF.")
    parser.add_argument("--nir", required=True, help="Path to the NIR-band GeoTIFF.")
    parser.add_argument("--scene-id", required=True, help="Stable identifier for this scene.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="NDWI water-detection threshold from -1.0 to 1.0 (default: 0.20).",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Print a JSON scene report to standard output and return a status code."""

    parser = build_parser()
    args = parser.parse_args(arguments)

    try:
        scene = SatelliteScene(
            green_band=args.green,
            nir_band=args.nir,
            scene_id=args.scene_id,
        )
        report = create_scene_report(scene, threshold=args.threshold)
    except (FileNotFoundError, RasterioError, ValueError) as error:
        parser.error(str(error))

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
