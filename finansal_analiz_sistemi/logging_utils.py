"""Helpers for counting log messages during execution."""

import logging
from datetime import datetime

ERROR_COUNTER: dict[str, int] = {"errors": 0, "warnings": 0}


class ErrorCountingFilter(logging.Filter):
    """Count ERROR and WARNING logs and store encountered error messages."""

    def __init__(self) -> None:
        super().__init__("counter")
        self.errors = 0
        self.warnings = 0
        self.error_list: list[tuple[str, str, str]] = []

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Increment counters and keep a list of error messages."""
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
