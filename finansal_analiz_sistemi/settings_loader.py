from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .config import get_settings_path

logger = logging.getLogger(__name__)


def load_settings(path: str | None = None) -> dict:
    """Load YAML settings from detected path."""
    settings_path = get_settings_path(path)
    if not Path(settings_path).exists():
        raise RuntimeError(f"settings.yaml not found at {settings_path}")
    with open(settings_path) as fh:
        return yaml.safe_load(fh) or {}
