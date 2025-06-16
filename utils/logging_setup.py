import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class NoDuplicateFilter(logging.Filter):
    """Filter that removes consecutive duplicate log messages."""

    def __init__(self):
        super().__init__("no-dup")
        self.last = None

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        current = (record.levelno, record.getMessage())
        if current == self.last:
            return False
        self.last = current
        return True


class CounterFilter(logging.Filter):
    """Counts warnings and errors for summary reporting."""

    def __init__(self):
        super().__init__("counter")
        self.errors = 0
        self.warnings = 0
        self.error_list: list[tuple[str, str, str]] = []

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        if record.levelno == logging.ERROR:
            self.errors += 1
            self.error_list.append(
                (datetime.now().isoformat(timespec="seconds"), "ERROR", record.getMessage())
            )
        elif record.levelno == logging.WARNING:
            self.warnings += 1
        return True


_counter_filter = CounterFilter()


def setup_logger(level: int = logging.INFO) -> CounterFilter:
    """Configure root logger with console and rotating file handlers."""
    root = logging.getLogger()
    if root.handlers:
        return _counter_filter

    log_dir = os.path.join("cikti", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"app_{datetime.now():%Y%m%d_%H%M%S}.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    console_handler = logging.StreamHandler(sys.stdout)

    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)
        handler.addFilter(NoDuplicateFilter())
        handler.addFilter(_counter_filter)

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])
    return _counter_filter


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger."""
    return logging.getLogger(name)
