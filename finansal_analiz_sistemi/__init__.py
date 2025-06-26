"""Package exports for convenience."""

import datetime as dt
import logging
import pathlib
from importlib import import_module

from finansal_analiz_sistemi.log_tools import setup_logging as _setup_logging

_log_dir = pathlib.Path("log")
_log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=_log_dir / f"run_{dt.date.today()}.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

config = import_module("config")
logging_config = import_module("finansal_analiz_sistemi.logging_config")

_setup_logging()

__all__ = ["config", "logging_config"]
