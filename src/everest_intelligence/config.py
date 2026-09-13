from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """
    Central application settings.

    Values are loaded from environment variables when available.
    No secrets are stored in source code.
    """

    project_name: str = "Everest Intelligence"
    environment: str = os.getenv("EVEREST_ENVIRONMENT", "development")
    ndwi_threshold: float = float(
        os.getenv("EVEREST_NDWI_THRESHOLD", "0.20")
    )
    log_level: str = os.getenv("EVEREST_LOG_LEVEL", "INFO")

    data_directory: Path = PROJECT_ROOT / "data"
    raw_data_directory: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_directory: Path = PROJECT_ROOT / "data" / "processed"


settings = Settings()
