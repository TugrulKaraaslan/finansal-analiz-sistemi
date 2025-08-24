from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import pandera as pa

# ---------------------------------------------------------------------------
# Alias configuration
# ---------------------------------------------------------------------------
_ALIAS_PAIRS: Dict[str, List[str]] = {
    # price series
    "date": ["tarih", "tarihi"],
    "open": [
        "open",
        "acilis",
        "açılış",
        "açilis",
        "açilis_fiyati",
        "açilis_fiyati_",
    ],
    "high": ["high", "yuksek", "yüksek"],
    "low": ["low", "dusuk", "düşük"],
    "close": [
        "close",
        "kapanis",
        "kapanış",
        "son",
        "son_fiyat",
        "adj_close",
        "kapanis_fiyati",
        "kapanis_fiyat",
    ],
    "volume": ["volume", "hacim", "islem_hacmi", "işlem_hacmi", "adet", "lot"],
    # indicators (example subset, extend as needed)
    "ema_20": ["EMA20", "EMA_20", "ema20"],
    "ema_10": ["EMA10", "EMA_10", "ema10"],
    "sma_50": ["SMA50", "SMA_50", "sma50"],
    "rsi_14": ["RSI14", "RSI_14", "rsi14"],
    "adx_14": ["ADX14", "ADX_14", "ADX_14.1"],
    "dmp_14": ["positivedirectionalindicator_14", "DMP_14.1"],
    "dmn_14": ["negativedirectionalindicator_14", "DMN_14.1"],
    "stoch_k": [
        "STOCHK",
        "STOCH_k",
        "stochK",
        "stoch %k",
        "stoch%k",
        "STOCHk_14_3_3",
        "STOCHk_14_3_3.1",
    ],
    "stoch_d": [
        "STOCHD",
        "stochD",
        "stoch %d",
        "stoch%d",
        "STOCHd_14_3_3",
        "STOCHd_14_3_3.1",
    ],
    "stochrsi_k": [
        "STOCHRSIk",
        "STOCHRSI_k",
        "stochrsi %k",
        "stochrsi%k",
        "STOCHRSIk_14_14_3_3",
        "STOCHRSIk_14_14_3_3.1",
    ],
    "stochrsi_d": [
        "STOCHRSId",
        "STOCHRSI_d",
        "stochrsi %d",
        "stochrsi%d",
        "STOCHRSId_14_14_3_3",
        "STOCHRSId_14_14_3_3.1",
    ],
    "macd_line": [
        "MACD",
        "MACD_12_26_9",
        "MACD 12,26,9",
        "macd12269",
        "macd 12 26 9",
    ],
    "macd_signal": [
        "MACDS",
        "MACDS_12_26_9",
        "MACD_SIGNAL",
        "MACD Signal",
        "macds 12,26,9",
    ],
    "bbm": ["BOLLINGER", "BOLLINGER_M", "Bollinger", "Bollinger_M", "bb_m"],
    "bbu": [
        "BOLLINGER_UPPER",
        "Bollinger_Upper",
        "BOLLINGERHIGH",
        "bb_u",
        "bb_upper",
    ],
    "bbl": [
        "BOLLINGER_LOWER",
        "Bollinger_Lower",
        "BOLLINGERLOW",
        "bb_l",
        "bb_lower",
    ],
    # extended mappings for new dataset columns
    "weighted_avg": ["agirlikli_ortalama"],
    "quantity": ["miktar"],
    # Bollinger band variants with decimal parameters
    "bbm_20_2": ["BBM_20_2.0", "BBM_20_2.0.1", "BBM_20_2.0.2"],
    "bbu_20_2": ["BBU_20_2.0", "BBU_20_2.0.1"],
    # MACD duplicates
    "macd_12_26_9": ["MACD_12_26_9.1"],
    "macds_12_26_9": ["MACDs_12_26_9.1"],
    # Ichimoku components
    "ichimoku_conversionline": ["ITS_9", "ITS_9.1"],
    "ichimoku_baseline": ["IKS_26", "IKS_26.1"],
    "ichimoku_leadingspana": ["ISA_9", "ISA_9.1"],
    "ichimoku_leadingspanb": ["ISB_26", "ISB_26.1"],
    # ADX and directionals with duplicate suffixes
    "aroon_up_14": ["aroonu_14", "AROONU_14.1", "aroonu_14_1"],
    "aroon_down_14": ["aroond_14", "AROOND_14.1", "aroond_14_1"],
    # weekly change column
    "change_1w_percent": ["change_1_w_percent"],
}


def _base_norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.casefold()
    s = re.sub(r"[\s\-.]+", "_", s)
    s = re.sub(r"(?<=[a-z])(?=\d)", "_", s)
    s = re.sub(r"(?<=\d)(?=[a-z])", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _alias_key(s: str) -> str:
    return _base_norm(s).replace("_", "")


LEGACY_MAP: Dict[str, str] = {}
for canon, aliases in _ALIAS_PAIRS.items():
    for alias in [canon] + aliases:
        LEGACY_MAP[_alias_key(alias)] = canon

CANONICAL_NAMES = set(LEGACY_MAP.values())

_CANONICAL_PATTERNS = [
    re.compile(r"^ema_\d+$"),
    re.compile(r"^sma_\d+$"),
    re.compile(r"^rsi_\d+$"),
    re.compile(r"^adx_\d+$"),
    re.compile(r"^dmp_\d+$"),
    re.compile(r"^dmn_\d+$"),
    re.compile(r"^roc_\d+$"),
    re.compile(r"^momentum_\d+$"),
    re.compile(r"^stoch_[kd]$"),
    re.compile(r"^stochrsi_[kd]$"),
    re.compile(r"^atr_\d+$"),
    re.compile(r"^bb[uml]_\d+_\d+$"),
    re.compile(r"^cci_\d+_[0-9_]+$"),
    re.compile(r"^change_\d+_[hdw]_percent$"),
    re.compile(r"^classicpivots_\d+[hd]_p$"),
    re.compile(r"^cmf_\d+$"),
    re.compile(r"^dcm_\d+_\d+$"),
    re.compile(r"^hma_\d+$"),
    re.compile(r"^ichimoku_(?:baseline|conversionline|leadingspana|leadingspanb)$"),
    re.compile(r"^macd_\d+_\d+_\d+$"),
    re.compile(r"^macds_\d+_\d+_\d+$"),
    re.compile(r"^mfi_\d+$"),
    re.compile(r"^mom_\d+$"),
    re.compile(r"^psarl_[0-9_]+$"),
    re.compile(r"^relative_volume$"),
    re.compile(r"^vwap_[a-z]+$"),
    re.compile(r"^vwma_\d+$"),
    re.compile(r"^willr_\d+$"),
    re.compile(r"^aroon_down_\d+$"),
    re.compile(r"^aroon_up_\d+$"),
]


def is_snake_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", name))


def _is_known_canonical(name: str) -> bool:
    if name in CANONICAL_NAMES:
        return True
    return any(p.fullmatch(name) for p in _CANONICAL_PATTERNS)


def _normalize_with_status(name: str, alias_map: Dict[str, str]) -> Tuple[str, bool]:
    base = _base_norm(name)
    key = _alias_key(name)
    result = alias_map.get(key, base)
    recognized = _is_known_canonical(result)
    return result, recognized


def normalize_name(name: str) -> str:
    result, _ = _normalize_with_status(name, LEGACY_MAP)
    if not is_snake_case(result):
        raise ValueError(f"normalized name '{result}' is not snake_case")
    return result


def normalize_columns(
    df: pd.DataFrame,
    extra_aliases: Optional[Dict[str, Iterable[str] | str]] = None,
    *,
    strict: bool = False,
) -> Tuple[pd.DataFrame, List[str]]:
    alias_map = LEGACY_MAP.copy()
    if extra_aliases:
        for canon, aliases in extra_aliases.items():
            canon_norm = normalize_name(canon)
            if isinstance(aliases, str):
                aliases = [aliases]
            for a in aliases:
                alias_map[_alias_key(a)] = canon_norm
            alias_map[_alias_key(canon_norm)] = canon_norm
    rename_map: Dict[str, str] = {}
    seen: set[str] = set()
    drops: List[str] = []
    unrecognized: List[str] = []
    for col in df.columns:
        norm, recognized = _normalize_with_status(col, alias_map)
        if norm in seen:
            drops.append(col)
            continue
        rename_map[col] = norm
        seen.add(norm)
        if not recognized:
            unrecognized.append(norm)
    out = df.rename(columns=rename_map).drop(columns=drops)
    if strict and unrecognized:
        raise pa.errors.SchemaError(
            f"unrecognized columns: {', '.join(unrecognized)}",
            failure_cases=pd.DataFrame({"column": unrecognized}),
            check="column_names",
        )
    return out, unrecognized


def validate_columns_schema(
    df: pd.DataFrame,
    mode: str = "strict_fail",
    required: Optional[Iterable[str]] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    if required is None:
        required = ["open", "high", "low", "close", "volume"]
    df_norm, unrecognized = normalize_columns(df)
    schema = pa.DataFrameSchema(
        {c: pa.Column(dtype=None, required=True) for c in required}
    )
    schema.validate(df_norm)
    if mode == "strict_fail" and unrecognized:
        raise pa.errors.SchemaError(
            f"unrecognized columns: {', '.join(unrecognized)}",
            failure_cases=pd.DataFrame({"column": unrecognized}),
            check="column_names",
        )
    if mode == "auto_fix" and unrecognized:
        df_norm = df_norm.drop(columns=unrecognized, errors="ignore")
    return df_norm, unrecognized


normalize_token = normalize_name

__all__ = [
    "normalize_name",
    "normalize_columns",
    "validate_columns_schema",
    "is_snake_case",
    "normalize_token",
    "LEGACY_MAP",
]
