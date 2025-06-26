from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, Tuple

PCT_STEP = 10


class DuplicateFilter(logging.Filter):
    """Filter out repeated log messages within a time window."""

    def __init__(self, window: float = 2.0) -> None:
        super().__init__("duplicate")
        self.window = window
        self._seen: Dict[Tuple[int, str], float] = {}

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        now = time.monotonic()
        key = (record.levelno, record.getMessage())
        last = self._seen.get(key)
        self._seen[key] = now
        # purge old entries
        for k, ts in list(self._seen.items()):
            if now - ts > self.window:
                del self._seen[k]
        return last is None or (now - last) > self.window


class CounterFilter(logging.Filter):
    """Count warnings and errors for summary reporting."""

    def __init__(self) -> None:
        super().__init__("counter")
        self.errors = 0
        self.warnings = 0
        self.error_list: list[tuple[str, str, str]] = []

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if record.levelno == logging.ERROR:
            self.errors += 1
            self.error_list.append(
                (
                    datetime.now().isoformat(timespec="seconds"),
                    "ERROR",
                    record.getMessage(),
                )
            )
        elif record.levelno == logging.WARNING:
            self.warnings += 1
        return True


_counter_filter = CounterFilter()


def setup_logging(window: float = 2.0, pct_step: int = 10) -> logging.Logger:
    """Attach :class:`DuplicateFilter` to root logger and disable propagation."""

    global PCT_STEP
    PCT_STEP = max(1, pct_step)
    root = logging.getLogger()
    if not any(isinstance(f, DuplicateFilter) for f in root.filters):
        root.addFilter(DuplicateFilter(window))
    root.propagate = False
    return root


def setup_logger(level: int = logging.INFO) -> CounterFilter:
    """Configure root logger with console and rotating file handlers."""

    root = logging.getLogger()
    if root.handlers:
        return _counter_filter

    log_dir = os.path.join("loglar")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "rapor.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=2_000_000, backupCount=20, encoding="utf-8"
    )
    console_handler = logging.StreamHandler(sys.stdout)

    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)
        handler.addFilter(DuplicateFilter())
        handler.addFilter(_counter_filter)

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])
    root.propagate = False
    return _counter_filter


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger."""

    return logging.getLogger(name)
