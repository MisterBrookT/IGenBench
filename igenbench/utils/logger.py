"""Simple logging utilities for nanochart."""

import logging
import sys
import traceback


def setup_logger(name: str = "nanochart", level: str = "INFO") -> logging.Logger:
    """Set up a simple logger with file and line info."""
    logger = logging.getLogger(name)
    logger.handlers.clear()

    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Simple formatter with file:line info
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False
    return logger


def log_error(logger: logging.Logger, message: str) -> None:
    """Log error with traceback."""
    logger.error(message)
    logger.error(traceback.format_exc())


# Default logger
logger = setup_logger()
