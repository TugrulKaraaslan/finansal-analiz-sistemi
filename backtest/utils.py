# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from pathlib import Path
from typing import Optional  # TİP DÜZELTİLDİ
import re
import unicodedata

from loguru import logger

from utils.paths import resolve_path


def ensure_dir(path: str | Path):
    p = resolve_path(path)
    target = p if not p.suffix else p.parent
    target.mkdir(parents=True, exist_ok=True)


def info(msg: str):
    logger.info(msg)


def normalize_key(s: Optional[str]) -> str:  # TİP DÜZELTİLDİ
    if s is None:
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
