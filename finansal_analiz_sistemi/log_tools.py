from __future__ import annotations

import logging
import time
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


def setup_logging(window: float = 2.0, pct_step: int = 10) -> logging.Logger:
    """Attach :class:`DuplicateFilter` to root logger and disable propagation."""

    global PCT_STEP
    PCT_STEP = max(1, pct_step)
    root = logging.getLogger()
    if not any(isinstance(f, DuplicateFilter) for f in root.filters):
        root.addFilter(DuplicateFilter(window))
    root.propagate = False
    return root
