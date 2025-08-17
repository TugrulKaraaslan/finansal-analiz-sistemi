from __future__ import annotations
import re
from typing import Dict, Iterable

_TURK = str.maketrans(
    {
        "ı": "i",
        "İ": "i",
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    }
)


def canonicalize(name: str) -> str:
    x = name.translate(_TURK).strip().lower()
    x = x.replace("%", "pct")
    x = re.sub(r"[^\w]+", "_", x)  # boşluk, nokta vs. → _
    x = re.sub(r"_+", "_", x).strip("_")
    # Özel: bollinger 20,2.0 → 20_2
    x = x.replace("_2_0", "_2")
    return x


ALIASES: Dict[str, str] = {
    # Bollinger varyasyonları
    "bbm_20_2_0": "bbm_20_2",
    "bbl_20_2_0": "bbl_20_2",
    "bbu_20_2_0": "bbu_20_2",
    # ADX/directionals
    "adx_14": "adx_14",
    "adx14": "adx_14",
    "adx": "adx_14",
    "adx_": "adx_14",
    "positivedirectionalindicator_14": "dmp_14",
    "negativedirectionalindicator_14": "dmn_14",
    # Stoch
    "stochk_14_3_3": "stoch_k",
    "stochd_14_3_3": "stoch_d",
    "stochrsik_14_14_3_3": "stochrsi_k",
    "stochrsid_14_14_3_3": "stochrsi_d",
    # Ichimoku kısa adlar (opsiyonel)
    "its_9": "ichimoku_conversionline",
    "iks_26": "ichimoku_baseline",
    "isa_9": "ichimoku_leadingspana",
    "isb_26": "ichimoku_leadingspanb",
    # Temeller
    "agirlikli_ortalama": "weighted_avg",
    "miktar": "quantity",
    # Price aliases
    "date": "date",
    "tarih": "date",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "kapanis": "close",
    "kapanis_fiyat": "close",
    "kapanis_fiyati": "close",
    "volume": "volume",
    "vol": "volume",
    "miktar_hacim": "volume",
    "islem_hacmi": "volume",
}


def canonical_map(columns: Iterable[str]) -> Dict[str, str]:
    """{canon: original} map"""
    out: Dict[str, str] = {}
    for c in columns:
        can = canonicalize(c)
        can = ALIASES.get(can, can)
        out.setdefault(can, c)
    return out
