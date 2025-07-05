"""Package exports with lazy submodule loading."""

from __future__ import annotations

import importlib
import types
from logging.config import dictConfig
from pathlib import Path

import yaml

from . import config, logging_config
from .logging_utils import ErrorCountingFilter

__all__ = ["config", "logging_config", "cache_builder", "data_loader"]

# Load logging configuration at import time if available
_yaml_path = Path(__file__).resolve().parent.parent / "logging_config.yaml"
if _yaml_path.exists():
    with _yaml_path.open(encoding="utf-8") as fh:
        dictConfig(yaml.safe_load(fh))


def __getattr__(name: str) -> types.ModuleType:
    if name in {"cache_builder", "data_loader"}:
        module = importlib.import_module(name)
        globals()[name] = module
        return module
    raise AttributeError(name)
