from __future__ import annotations
import re
from typing import Iterable, Dict
from .canonical import CANONICAL_SET

_SNAKE_RE1 = re.compile(r"[^0-9A-Za-z]+")
_SNAKE_RE2 = re.compile(r"_{2,}")


def to_snake(s: str) -> str:
    s = s.strip()
    translit = str.maketrans(
        {
            "ı": "i",
            "İ": "I",
            "ğ": "_g",
            "Ğ": "_G",
            "ş": "s",
            "Ş": "S",
            "ö": "o",
            "Ö": "O",
            "ü": "u",
            "Ü": "U",
            "ç": "c",
            "Ç": "C",
        }
    )
    s = s.translate(translit)
    s = _SNAKE_RE1.sub("_", s)
    s = _SNAKE_RE2.sub("_", s)
    s = s.strip("_")
    return s.lower()


def normalize_indicator_token(
    token: str, alias_map: Dict[str, str] | None = None
) -> str:
    # 1) alias çöz; 2) snake; 3) kanonik set kontrolü gerekirse üst katmanda yapılır
    raw = token
    if alias_map and raw in alias_map:
        raw = alias_map[raw]
    norm = to_snake(raw)
    return norm


def normalize_dataframe_columns(
    columns: Iterable[str], alias_map: Dict[str, str] | None = None
) -> Dict[str, str]:
    """Girdi kolon adlarını kanonik/snake_case'e map eder.
    Dönüş: {orijinal: yeni_ad}
    Not: Çakışmayı üst katman kontrol edecek (ör. A4 dry-run'da).
    """
    result: Dict[str, str] = {}
    seen: set[str] = set()
    for col in columns:
        new = normalize_indicator_token(col, alias_map)
        # ör. 'Adj Close' -> 'close'
        if new in seen:
            # üst katmanda VC00X ile yakalanacak; burada sadece map'i dönderiyoruz
            pass
        seen.add(new)
        result[col] = new
    return result
