import logging

ERROR_COUNTER: dict[str, int] = {"errors": 0, "warnings": 0}


class ErrorCountingFilter(logging.Filter):
    """ERROR/WARNING satırlarını sayaçlar."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno >= logging.ERROR:
            ERROR_COUNTER["errors"] += 1
        elif record.levelno == logging.WARNING:
            ERROR_COUNTER["warnings"] += 1
        return True
