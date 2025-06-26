"""Logging configuration with optional rich handling."""

from __future__ import annotations

import logging
import os
import sys
from typing import Final, List

try:
    from rich.console import Console
    from rich.logging import RichHandler

    _HAVE_RICH: Final[bool] = True
except ImportError:  # pragma: no cover – rich is optional
    Console = None  # type: ignore
    RichHandler = None  # type: ignore
    _HAVE_RICH = False

from finansal_analiz_sistemi import config


def _want_rich() -> bool:
    """Return True if rich logging should be enabled."""
    # Disable if user forces simple logs
    if os.getenv("LOG_SIMPLE"):
        return False

    # If rich not installed, bail early
    if not _HAVE_RICH:
        return False

    # Use rich in Colab or when stderr is None (piped)
    return config.IS_COLAB or sys.stderr is None


def setup_logging() -> logging.Logger:
    """Configure root logger and return it."""
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level)
        return root

    handlers: List[logging.Handler] = []
    if _want_rich():
        console = Console()
        rich_handler = RichHandler(
            console=console,
            show_time=False,
            rich_tracebacks=True,
        )
        handlers.append(rich_handler)
    else:
        handlers.append(logging.StreamHandler())

    root.setLevel(level)
    for handler in handlers:
        root.addHandler(handler)

    return root
