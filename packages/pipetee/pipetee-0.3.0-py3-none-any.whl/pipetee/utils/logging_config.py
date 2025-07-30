import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    logger_name: str,
    log_level: int = logging.INFO,
    log_dir: str = "logs",
    log_format: Optional[str] = None,
) -> logging.Logger:
    """Configure a logger with file and console handlers"""

    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Default format if none provided
    if log_format is None:
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)-30s | "
            "%(funcName)-20s | Line:%(lineno)-4d | %(message)s"
        )

    formatter = logging.Formatter(log_format)

    # File handler with daily rotation, keeping 7 days of history
    file_handler = TimedRotatingFileHandler(
        filename=log_path / f"{logger_name}.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
