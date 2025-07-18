"""Map exceptions to user-friendly reason/hint pairs.

This lightweight table translates Python exception names into
localized ``(reason, hint)`` tuples so callers can present concise
error messages.
"""

from typing import Tuple

__all__ = ["get_reason_hint"]

# Mapping from exception names to localized (reason, hint) tuples.
REASON_MAP: dict[str, Tuple[str, str]] = {
    "ZeroDivisionError": (
        "S\u0131f\u0131ra B\u00f6lme",
        "B\u00f6l\u00fcnen de\u011feri s\u0131f\u0131rdan farkl\u0131 yap",
    ),
    "KeyError": (
        "Veri Alan\u0131 Yok",
        "hisse_kodu / tarih s\u00fctunu eksik olabilir",
    ),
    "FileNotFoundError": (
        "Dosya Bulunamad\u0131",
        "Ge\u00e7erli bir dosya yolu belirtin",
    ),
    "ValueError": (
        "Ge\u00e7ersiz De\u011fer",
        "Parametreleri kontrol edin",
    ),
}

DEFAULT_REASON: Tuple[str, str] = ("Bilinmeyen Hata", "Detay i\u00e7in loglara bak")


def get_reason_hint(exc: Exception, _locale: str = "tr") -> Tuple[str, str]:
    """Return a user-friendly reason/hint pair for ``exc``.

    Args:
        exc (Exception): Exception instance to map.
        _locale (str, optional): Reserved for future localization and
            currently ignored.

    Returns:
        Tuple[str, str]: ``(reason, hint)`` describing the failure.
    """
    return REASON_MAP.get(type(exc).__name__, DEFAULT_REASON)
