"""Shared logging setup for the api and ingest processes."""
import logging
import os

_CONFIGURED = False
_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    raw_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = raw_level if raw_level in _VALID_LEVELS else "INFO"
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if level != raw_level:
        logging.getLogger(__name__).warning(
            "Invalid LOG_LEVEL=%r, falling back to INFO", raw_level
        )
    _CONFIGURED = True
