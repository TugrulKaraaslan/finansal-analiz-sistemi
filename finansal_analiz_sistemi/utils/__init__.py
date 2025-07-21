"""Convenience wrappers for internal helper modules.

The package exposes commonly used utilities like ``swapaxes`` and
``normalize_filtre_kodu`` so they can be imported from a single location.
"""

from __future__ import annotations

from .compat import transpose as swapaxes
from .normalize import normalize_filtre_kodu

__all__ = ["swapaxes", "normalize_filtre_kodu"]
