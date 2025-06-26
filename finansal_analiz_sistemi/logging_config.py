import logging
import os
import sys

try:
    from rich.console import Console
    from rich.logging import RichHandler

    _HAVE_RICH = True
except ImportError:  # pragma: no cover - rich is optional
    Console = None  # type: ignore
    RichHandler = None  # type: ignore
    _HAVE_RICH = False

from finansal_analiz_sistemi import config


def _want_rich() -> bool:
    if os.getenv("LOG_SIMPLE"):
        return False
    if not _HAVE_RICH:
        return False
    return config.IS_COLAB or sys.stderr is None


def setup_logging() -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    level_num = getattr(logging, level, logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level_num)
        return root

    handlers: list[logging.Handler] = []
    if _want_rich():
        console = Console()
        rich_handler = RichHandler(
            console=console, show_time=False, rich_tracebacks=True
        )
        handlers.append(rich_handler)
    else:
        handlers.append(logging.StreamHandler())

    root.setLevel(level_num)
    for h in handlers:
        root.addHandler(h)

    return root


def get_logger(name: str) -> logging.Logger:
    root = setup_logging()
    logger = logging.getLogger(name)
    if not logger.handlers:
        for handler in root.handlers:
            logger.addHandler(handler)
        logger.propagate = True
    return logger
