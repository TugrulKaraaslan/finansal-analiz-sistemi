"""Helpers for counting log messages during execution."""

import logging

ERROR_COUNTER: dict[str, int] = {"errors": 0, "warnings": 0}


class ErrorCountingFilter(logging.Filter):
    """Count ERROR and WARNING logs."""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Increment global counters and allow the record."""
        if record.levelno >= logging.ERROR:
            ERROR_COUNTER["errors"] += 1
        elif record.levelno == logging.WARNING:
            ERROR_COUNTER["warnings"] += 1
        return True
