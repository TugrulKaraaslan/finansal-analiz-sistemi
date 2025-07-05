"""Package exports with lazy submodule loading."""

from __future__ import annotations

import importlib
import types

from . import config, logging_config

__all__ = ["config", "logging_config", "cache_builder", "data_loader"]


def __getattr__(name: str) -> types.ModuleType:
    if name in {"cache_builder", "data_loader"}:
        module = importlib.import_module(name)
        globals()[name] = module
        return module
    raise AttributeError(name)
