"""
Logging configuration.

Creates logs/ directory with separate log files by type,
automatically cleans up logs older than 1 day.
"""

import logging
import sys
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path


def clean_old_logs(log_dir: Path, max_age_days: int = 1) -> None:
    """
    Remove log files older than max_age_days.

    Args:
        log_dir: Directory containing logs
        max_age_days: Maximum age in days to keep (default: 1)
    """
    if not log_dir.exists():
        return

    cutoff = time.time() - (max_age_days * 86400)

    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff:
            try:
                log_file.unlink()
            except Exception:
                pass


def configure_logging(level: int = logging.INFO, log_dir: str = "logs") -> None:
    """
    Configure application logging with file output organized by directory.

    Creates logs/ directory with separate log files, auto-cleans logs older than 1 day.

    Args:
        level: Logging level (default: INFO)
        log_dir: Base directory for logs (default: "logs")
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Clean old logs on startup (keep only 1 day)
    clean_old_logs(log_path, max_age_days=1)

    # Log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console output (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File output for all logs
    main_log_file = log_path / "app.log"
    file_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # Create separate log files by category
    categories = ["api", "chat", "error"]
    for category in categories:
        category_logger = logging.getLogger(category)
        category_logger.setLevel(level)
        category_logger.propagate = True  # Still propagate to root logger

        category_log_file = log_path / f"{category}.log"
        category_handler = RotatingFileHandler(
            category_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        category_handler.setFormatter(formatter)
        category_logger.addHandler(category_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
