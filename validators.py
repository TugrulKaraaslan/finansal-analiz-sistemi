"""Validation utilities for structured error reporting.

The module exposes :class:`ValidationError` so helpers can return
consistent error objects instead of bare strings.
"""

from dataclasses import dataclass

__all__ = ["ValidationError"]


@dataclass
class ValidationError:
    """Structured information about a validation failure.

    Attributes
    ----------
    hata_tipi : str
        Short code identifying the error type.
    eksik_ad : str
        Name of the missing or invalid field.
    detay : str
        Detailed explanation of the issue.
    cozum_onerisi : str
        Suggested resolution for the user.
    reason : str
        Localized failure reason.
    hint : str
        Localized hint to assist recovery.

    """

    hata_tipi: str
    eksik_ad: str
    detay: str
    cozum_onerisi: str
    reason: str
    hint: str
