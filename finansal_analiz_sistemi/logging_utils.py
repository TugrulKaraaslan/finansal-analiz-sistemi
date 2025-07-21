"""Utilities to track log messages during execution.

The module exposes :class:`ErrorCountingFilter` which counts ERROR and
WARNING records so tests and scripts can assert on logged output.
"""

from __future__ import annotations

import logging
from datetime import datetime

ERROR_COUNTER: dict[str, int] = {"errors": 0, "warnings": 0}


class ErrorCountingFilter(logging.Filter):
    """Count ERROR and WARNING logs and store encountered error messages."""

    def __init__(self) -> None:
        """Initialize counters and an internal error list."""
        super().__init__("counter")
        self.errors = 0
        self.warnings = 0
        self.error_list: list[tuple[str, str, str]] = []

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Increment counters and keep a list of error messages.

        Args:
            record (logging.LogRecord): The log record being handled.

        Returns:
            bool: Always ``True`` to allow processing to continue.

        """
        if record.levelno >= logging.ERROR:
            ERROR_COUNTER["errors"] += 1
            self.errors += 1
            self.error_list.append(
                (
                    datetime.now().isoformat(timespec="seconds"),
                    "ERROR",
                    record.getMessage(),
                )
            )
        elif record.levelno == logging.WARNING:
            ERROR_COUNTER["warnings"] += 1
            self.warnings += 1
        return True
