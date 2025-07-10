"""Load runtime configuration from ``settings.yaml``.

The file location can be overridden with the ``FAS_SETTINGS_FILE``
environment variable.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAX_FILTER_DEPTH = 15
FALLBACK_MAX_FILTER_DEPTH = 7


def _load_cfg() -> dict[str, Any]:
    """Load YAML configuration if available."""
    cfg_file = Path(
        os.environ.get("FAS_SETTINGS_FILE", Path(__file__).with_suffix(".yaml"))
    )
    if cfg_file.is_file():
        try:
            with cfg_file.open() as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {"max_filter_depth": FALLBACK_MAX_FILTER_DEPTH}
    return {}


_cfg = _load_cfg()


def _as_int(value: Any, default: int) -> int:
    """Return ``value`` cast to ``int`` or ``default`` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


value = _cfg.get("max_filter_depth")
if value is None:
    MAX_FILTER_DEPTH = DEFAULT_MAX_FILTER_DEPTH
else:
    MAX_FILTER_DEPTH = _as_int(value, FALLBACK_MAX_FILTER_DEPTH)

__all__ = ["MAX_FILTER_DEPTH"]
