from __future__ import annotations
import re
from typing import Iterable, Optional, Dict

_TURK_MAP = str.maketrans({
    "ı":"i","İ":"i","ç":"c","Ç":"c","ğ":"g","Ğ":"g","ö":"o","Ö":"o","ş":"s","Ş":"s","ü":"u","Ü":"u",
})

def canonicalize(name: str) -> str:
    x = name.translate(_TURK_MAP).lower()
    x = x.replace("%", "pct")
    x = re.sub(r"[^\w]+", "_", x)
    x = re.sub(r"_+", "_", x).strip("_")
    return x

ALIASES: Dict[str, str] = {
    "date": "date", "tarih": "date",
    "open": "open", "high": "high", "low": "low", "close": "close",
    "agirlikli_ortalama": "weighted_avg", "miktar": "quantity",
    "volume": "volume", "vol": "volume",
    "adx_14": "adx_14", "adx14": "adx_14", "adx": "adx_14",
    "dmp_14": "dmp_14", "dmn_14": "dmn_14",
    "positivedirectionalindicator_14": "dmp_14",
    "negativedirectionalindicator_14": "dmn_14",
    "aroond_14": "aroond_14", "aroonu_14": "aroonu_14",
    "stochk_14_3_3": "stochk_14_3_3", "stochd_14_3_3": "stochd_14_3_3",
    "stoch_k": "stochk_14_3_3", "stoch_d": "stochd_14_3_3",
    "stochrsik_14_14_3_3": "stochrsik_14_14_3_3",
    "stochrsid_14_14_3_3": "stochrsid_14_14_3_3",
    "rsi_14": "rsi_14", "rsi7": "rsi_7", "rsi_7": "rsi_7",
    "macd_line": "macd_line", "macd_signal": "macd_signal",
}

def canonical_map(columns: Iterable[str]) -> Dict[str, str]:
    out = {}
    for c in columns:
        can = canonicalize(c)
        can = ALIASES.get(can, can)
        out.setdefault(can, c)
    return out

def pick(colmap: Dict[str, str], *candidates: str) -> Optional[str]:
    for cand in candidates:
        cand = ALIASES.get(canonicalize(cand), canonicalize(cand))
        if cand in colmap:
            return colmap[cand]
    return None
