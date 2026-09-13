from __future__ import annotations

import logging
import sys

from src.everest_intelligence.config import settings


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Logs are written to the terminal.
    Sensitive values must never be written to logs.
    """
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for the requested module.
    """
    return logging.getLogger(name)
