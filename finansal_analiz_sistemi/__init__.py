"""Initialize the ``finansal_analiz_sistemi`` package.

Loading this package applies logging configuration from
``logging_config.yaml`` and exposes certain submodules lazily so that heavy
imports happen only when needed.
"""

from __future__ import annotations

import importlib
import logging.config
import types
from pathlib import Path

import yaml

# Import solely for side effects so YAML-based log filters are registered.
from .logging_utils import ErrorCountingFilter  # noqa: F401

# Configure logging via YAML at package import time
base = Path(__file__).resolve().parent.parent
(base / "loglar").mkdir(exist_ok=True)
with open(base / "logging_config.yaml", "r", encoding="utf-8") as fh:
    logging.config.dictConfig(yaml.safe_load(fh))

from . import config, logging_config  # noqa: E402

__all__ = ["cache_builder", "config", "data_loader", "logging_config"]


def __getattr__(name: str) -> types.ModuleType:
    """Import and return the requested submodule on first access.

    Args:
        name: Name of the submodule to import.

    Returns:
        ModuleType: The imported module.

    Raises:
        AttributeError: If ``name`` is not a known submodule.
    """
    if name in {"cache_builder", "data_loader"}:
        module = importlib.import_module(name)
        globals()[name] = module
        return module
    raise AttributeError(name)
