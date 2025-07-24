from __future__ import annotations

import os

__all__ = ["positive_int_env"]


def positive_int_env(name: str, default: int) -> int:
    """Return a positive integer from ``name`` or ``default`` when invalid."""
    val = os.getenv(name)
    if val is None:
        return default
    try:
        num = int(val)
    except ValueError:
        return default
    return num if num > 0 else default
