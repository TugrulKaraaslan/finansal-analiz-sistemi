"""Map exceptions to user friendly reason/hint pairs.

Provides a lightweight translation layer from Python exception names to
localized error messages.
"""

from typing import Dict, Tuple

__all__ = ["get_reason_hint"]

REASON_MAP: Dict[str, Tuple[str, str]] = {
    "ZeroDivisionError": (
        "S\u0131f\u0131ra B\u00f6lme",
        "B\u00f6l\u00fcnen de\u011feri s\u0131f\u0131rdan farkl\u0131 yap",
    ),
    "KeyError": (
        "Veri Alan\u0131 Yok",
        "hisse_kodu / tarih s\u00fctunu eksik olabilir",
    ),
}

DEFAULT_REASON: Tuple[str, str] = ("Bilinmeyen Hata", "Detay i\u00e7in loglara bak")


def get_reason_hint(exc: Exception, _locale: str = "tr") -> Tuple[str, str]:
    """Return a user friendly reason/hint tuple for given exception."""
    # ``locale`` is reserved for future localization support
    return REASON_MAP.get(type(exc).__name__, DEFAULT_REASON)
