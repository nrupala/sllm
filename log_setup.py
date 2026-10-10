"""Central logging setup for SL-LLM.

Provides a single ``setup_logging`` entry point so every module gets a
consistently formatted logger instead of ad-hoc ``print`` calls.
"""

import logging
import sys
from pathlib import Path

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Configure the root logger for SL-LLM and return the package logger.

    Args:
        level: Logging level name (e.g. "INFO", "DEBUG").
        log_file: Optional path to also tee log records into a file.

    Returns:
        The ``sllm`` logger instance.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=_DEFAULT_FORMAT,
        datefmt=_DEFAULT_DATE_FORMAT,
        handlers=handlers,
        force=True,
    )
    return logging.getLogger("sllm")


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``sllm`` namespace."""
    return logging.getLogger(f"sllm.{name}")
