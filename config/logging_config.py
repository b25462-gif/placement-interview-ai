"""
Logging configuration using loguru.
"""

import sys
from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    logger.remove()  # Remove default handler

    # Console handler — colorized
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler — rotating
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info("Logging initialized at level: {}", level)


__all__ = ["setup_logging", "logger"]
