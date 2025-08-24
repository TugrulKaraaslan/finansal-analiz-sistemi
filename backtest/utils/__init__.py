from __future__ import annotations

import math
import re
import unicodedata


def normalize_key(s: str | float | None) -> str:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return ""
    s = str(s).strip()
    # Map Turkish specific chars to ASCII-ish
    table = str.maketrans(
        {
            "İ": "I",
            "I": "I",
            "ı": "i",
            "Ş": "S",
            "ş": "s",
            "Ğ": "G",
            "ğ": "g",
            "Ü": "U",
            "ü": "u",
            "Ö": "O",
            "ö": "o",
            "Ç": "C",
            "ç": "c",
        }
    )
    s = s.translate(table)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


__all__ = ["normalize_key"]
