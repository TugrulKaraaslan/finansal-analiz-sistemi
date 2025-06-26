"""Package exports for convenience."""

import pathlib
from importlib import import_module

from finansal_analiz_sistemi.log_tools import setup_logging as _setup_logging
from utils.logging_setup import setup_logger

_log_dir = pathlib.Path("loglar")
_log_dir.mkdir(exist_ok=True)
setup_logger()

config = import_module("config")
logging_config = import_module("finansal_analiz_sistemi.logging_config")

_setup_logging()

__all__ = ["config", "logging_config"]
