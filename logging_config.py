import logging
import os
import sys
from contextlib import suppress


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    level_num = getattr(logging, level, logging.INFO)

    # Renkli Rich handler (isteğe bağlı devre dışı)
    if not os.getenv("LOG_SIMPLE") and sys.stderr.isatty():
        with suppress(ImportError):
            from rich.logging import RichHandler

            logging.basicConfig(
                level=level_num,
                format="%(message)s",
                datefmt="[%X]",
                handlers=[RichHandler(markup=True)],
            )
            return

    # Fallback düz format
    logging.basicConfig(
        level=level_num,
        format="%(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger; auto-initialises root."""

    root = logging.getLogger()

    if not root.handlers:
        setup_logging()

    logger = logging.getLogger(name)

    if not logger.handlers:
        for handler in root.handlers:
            logger.addHandler(handler)
        logger.propagate = True

    return logger
