"""Simpler logging setup for local helpers."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

# ——— Config ———
LOG_DIR = os.getenv("LOG_DIR", "loglar")
os.makedirs(LOG_DIR, exist_ok=True)


def _create_handler() -> RotatingFileHandler:
    """Return a file handler with default rotation settings."""
    handler = RotatingFileHandler(
        f"{LOG_DIR}/run.log",
        maxBytes=2_000_000,  # 2 MB
        backupCount=3,  # run.log, .1, .2, .3
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    return handler


def setup_logging() -> logging.Logger:
    """Configure root logger with a rotating file handler."""

    root = logging.getLogger()
    for h in list(root.handlers):
        if isinstance(h, RotatingFileHandler):
            root.removeHandler(h)  # pragma: no cover - cleanup before reconfig
    handler = _create_handler()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    return root


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a named logger after ensuring the root is configured."""

    if (
        not logging.getLogger().handlers
    ):  # pragma: no cover - already configured in tests
        setup_logging()  # pragma: no cover
    return logging.getLogger(name)


setup_logging()

__all__ = ["get_logger", "setup_logging"]
