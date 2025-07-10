"""Validation utilities used across the project.

This module exposes :class:`ValidationError` for structured error
reporting.
"""

from dataclasses import dataclass

__all__ = ["ValidationError"]


@dataclass
class ValidationError:
    """Structured error information returned by validators."""

    hata_tipi: str
    eksik_ad: str
    detay: str
    cozum_onerisi: str
    reason: str
    hint: str
