"""Read ``settings.yaml`` and patch :mod:`settings` when present.

This module locates the configuration file using :func:`get_settings_path`
and applies recognized options (such as ``max_filter_depth``) to the runtime
``settings`` module if available.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .config import get_settings_path

logger = logging.getLogger(__name__)


def load_settings(path: str | None = None) -> dict:
    """Load YAML settings and apply known options to the ``settings`` module.

    Args:
        path (str | None): Optional path to ``settings.yaml``.

    Returns:
        dict: Parsed settings data.

    """
    settings_path = get_settings_path(path)
    if not Path(settings_path).exists():
        raise RuntimeError(f"settings.yaml not found at {settings_path}")

    with open(settings_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    try:  # pragma: no cover - best effort
        import settings as _settings

        max_depth = data.get("max_filter_depth")
        if isinstance(max_depth, int):
            _settings.MAX_FILTER_DEPTH = max_depth
    except Exception:
        logger.debug("Settings module not available for patching")

    return data


__all__ = ["load_settings"]
