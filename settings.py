from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAX_FILTER_DEPTH = 7


def _load_cfg() -> dict[str, Any]:
    """Load YAML configuration if available."""
    cfg_file = Path(
        os.environ.get("FAS_SETTINGS_FILE", Path(__file__).with_suffix(".yaml"))
    )
    if cfg_file.is_file():
        with cfg_file.open() as f:
            return yaml.safe_load(f) or {}
    return {}


_cfg = _load_cfg()


def _as_int(value: Any, default: int) -> int:
    """Return ``value`` cast to ``int`` or ``default`` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


MAX_FILTER_DEPTH: int = _as_int(_cfg.get("max_filter_depth"), DEFAULT_MAX_FILTER_DEPTH)

