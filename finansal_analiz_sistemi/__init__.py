"""Initialize :mod:`finansal_analiz_sistemi`.

Importing this package configures logging from ``logging_config.yaml``.
Heavy dependencies are loaded lazily so modules only import when needed.
"""

from __future__ import annotations

import importlib
import logging.config
import types
from pathlib import Path

import yaml

# Import for its side effect of registering YAML-based log filters.
from .logging_utils import ErrorCountingFilter as _ErrorCountingFilter  # noqa: F401

# Touch the alias so static analyzers register the import as used.
_unused_filter = _ErrorCountingFilter

# Configure logging via YAML at package import time
base = Path(__file__).resolve().parent.parent
(base / "loglar").mkdir(exist_ok=True)
yaml_cfg = base / "logging_config.yaml"
if yaml_cfg.exists():
    with yaml_cfg.open("r", encoding="utf-8") as fh:
        logging.config.dictConfig(yaml.safe_load(fh))
else:  # pragma: no cover - fallback when YAML missing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

from . import config, logging_config  # noqa: E402

__all__ = ["cache_builder", "config", "data_loader", "logging_config"]


def __getattr__(name: str) -> types.ModuleType:
    """Return the requested submodule, importing it on first access.

    Args:
        name (str): Name of the submodule to import.

    Returns:
        types.ModuleType: The imported module.

    Raises:
        AttributeError: If ``name`` is not a known submodule.

    """
    if name in {"cache_builder", "data_loader"}:
        module = importlib.import_module(name)
        globals()[name] = module
        return module
    raise AttributeError(name)
