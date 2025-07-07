"""Package exports with lazy submodule loading."""

from __future__ import annotations

import importlib
import logging.config
import types
from pathlib import Path

import yaml

# Import solely for side-effects (YAML filter resolution).  # noqa: F401
from .logging_utils import ErrorCountingFilter  # noqa: F401

# Configure logging from YAML at package import time
base = Path(__file__).resolve().parent.parent
(base / "loglar").mkdir(exist_ok=True)
with open(base / "logging_config.yaml", "r", encoding="utf-8") as fh:
    logging.config.dictConfig(yaml.safe_load(fh))

from . import config, logging_config  # noqa: E402

__all__ = ["config", "logging_config", "cache_builder", "data_loader"]


def __getattr__(name: str) -> types.ModuleType:
    if name in {"cache_builder", "data_loader"}:
        module = importlib.import_module(name)
        globals()[name] = module
        return module
    raise AttributeError(name)
