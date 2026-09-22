"""Validated metadata for Earth-observation scenes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SceneMetadata:
    """Scientific and provenance metadata describing one satellite scene."""

    platform: str
    sensor: str
    acquisition_datetime: datetime
    processing_level: str
    provider: str
    resolution_m: float
    cloud_cover_percent: float | None = None
    source_uri: str | None = None

    def __post_init__(self) -> None:
        """Validate metadata required for scientific traceability."""
        if not self.platform.strip():
            raise ValueError("Platform must not be empty.")

        if not self.sensor.strip():
            raise ValueError("Sensor must not be empty.")

        if not self.processing_level.strip():
            raise ValueError("Processing level must not be empty.")

        if not self.provider.strip():
            raise ValueError("Provider must not be empty.")

        if self.resolution_m <= 0:
            raise ValueError("Resolution must be greater than zero.")

        if self.cloud_cover_percent is not None and not (
            0.0 <= self.cloud_cover_percent <= 100.0
        ):
            raise ValueError("Cloud cover must be between 0 and 100 percent.")

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible metadata."""
        return {
            "platform": self.platform,
            "sensor": self.sensor,
            "acquisition_datetime": self.acquisition_datetime.isoformat(),
            "processing_level": self.processing_level,
            "provider": self.provider,
            "resolution_m": self.resolution_m,
            "cloud_cover_percent": self.cloud_cover_percent,
            "source_uri": self.source_uri,
        }
