"""Logging helpers used across the project.

This module configures rotating log files, suppresses repeated messages
and exposes an :class:`ErrorCountingFilter` so tests can assert on logged
warnings or errors.
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Tuple

from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.logging_config import setup_logging as _cfg_setup_logging
from finansal_analiz_sistemi.logging_utils import ErrorCountingFilter

PCT_STEP = 10


_counter_filter = ErrorCountingFilter()


class DuplicateFilter(logging.Filter):
    """Suppress duplicate log messages within a time window."""

    def __init__(self, window: float = 2.0) -> None:
        """Initialize the filter.

        Args:
            window (float, optional): Duration in seconds to suppress
                repeated messages.

        """
        super().__init__("duplicate")
        self.window = window
        self._seen: Dict[Tuple[int, str], float] = {}

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Allow a log record if it has not been seen recently.

        Messages are tracked by their level and text. A record is only emitted
        when no identical message was logged within the configured ``window``.

        Args:
            record (logging.LogRecord): Log record being processed.

        Returns:
            bool: ``True`` if the record should be emitted.

        """
        now = time.monotonic()
        key = (record.levelno, record.getMessage())
        last = self._seen.get(key)
        self._seen[key] = now
        # purge old entries
        for k, ts in list(self._seen.items()):
            if now - ts > self.window:
                del self._seen[k]
        return last is None or (now - last) > self.window


def setup_logger(level: int = logging.INFO) -> ErrorCountingFilter:
    """Configure the root logger for console and file output.

    Args:
        level (int, optional): Logging level.

    Returns:
        ErrorCountingFilter: Filter that tracks error and warning counts.

    """
    root = logging.getLogger()
    log_dir = Path("loglar")
    log_dir.mkdir(exist_ok=True)

    if root.handlers:
        root.setLevel(level)
        if not any(
            isinstance(h, (RotatingFileHandler, logging.FileHandler))
            and Path(getattr(h, "baseFilename", "")).parent == log_dir
            for h in root.handlers
        ):
            if config.IS_COLAB:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"colab_run_{timestamp}.log"
                fh = logging.FileHandler(log_file, encoding="utf-8")
            else:
                log_file = log_dir / "rapor.log"
                fh = RotatingFileHandler(
                    log_file, maxBytes=2_000_000, backupCount=20, encoding="utf-8"
                )
            fh.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
                )
            )
            fh.addFilter(DuplicateFilter())
            root.addHandler(fh)
        if _counter_filter not in root.filters:
            root.addFilter(_counter_filter)
        root.propagate = False
        return _counter_filter
    if config.IS_COLAB:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"colab_run_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
    else:
        log_file = log_dir / "rapor.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=2_000_000, backupCount=20, encoding="utf-8"
        )

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    console_handler = logging.StreamHandler(sys.stdout)

    if _counter_filter not in root.filters:
        root.addFilter(_counter_filter)
    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)
        handler.addFilter(DuplicateFilter())

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])
    root.propagate = False
    return _counter_filter


def setup_logging(window: float = 2.0, pct_step: int = 10) -> logging.Logger:
    """Initialize logging and attach a duplicate-message filter.

    Args:
        window (float, optional): Time window for duplicate suppression.
        pct_step (int, optional): Progress log step percentage.

    Returns:
        logging.Logger: The configured root logger.

    """
    global PCT_STEP
    PCT_STEP = max(1, pct_step)
    root = _cfg_setup_logging()
    if not any(isinstance(f, DuplicateFilter) for f in root.filters):
        root.addFilter(DuplicateFilter(window))
    root.propagate = False
    return root
