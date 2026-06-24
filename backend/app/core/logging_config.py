"""Logging configuration for the application."""

import logging
import sys
from typing import Optional

from .config import settings


class LoggingConfig:
    """Logging configuration manager."""

    @staticmethod
    def setup_logging(
        level: int = logging.INFO,
        log_format: Optional[str] = None,
        date_format: Optional[str] = None,
    ) -> None:
        """Configure application logging.

        Args:
            level: Logging level (default: INFO)
            log_format: Custom log format string
            date_format: Custom date format string
        """
        if log_format is None:
            log_format = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        if date_format is None:
            date_format = "%Y-%m-%d %H:%M:%S"

        # Configure root logger
        logging.basicConfig(
            level=level,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
            ],
        )

        # Set uvicorn loggers to match
        logging.getLogger("uvicorn").setLevel(level)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)