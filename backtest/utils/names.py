import re
from typing import Dict

# Normalization mode: off, smart, strict
_MODE = "smart"


def set_name_normalization(mode: str) -> None:
    """Set global name normalization mode."""
    global _MODE
    mode = str(mode).lower()
    if mode not in {"off", "smart", "strict"}:
        raise ValueError("invalid mode")
    _MODE = mode


# Genel normalize: küçük harf, boşluk/tire -> _, % -> percent, harf->sayı sınırına _ koy
def _base_norm(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("%", " percent ")
    s = re.sub(r"[^\w]+", "_", s)               # harf/rakam/altçizgi dışını altçizgi
    s = re.sub(r"(?<=[a-z])(?=\d)", "_", s)     # harf-sayı sınırına _
    s = re.sub(r"_+", "_", s).strip("_")        # fazlalıkları temizle
    return s


# Alias anahtarı: kanonik karşılaştırma için altçizgileri de kaldır
def _alias_key(s: str) -> str:
    return re.sub(r"[_\W]+", "", s.lower())


# Bilinen alias eşlemeleri (key -> canonical). Key oluşturulurken _ kaldırılır.
ALIAS: Dict[str, str] = {
    # EMA/SMA
    "ema5": "ema_5", "ema05": "ema_5", "ema_5": "ema_5",
    "ema10": "ema_10", "ema_10": "ema_10",
    "ema20": "ema_20", "ema_20": "ema_20",
    "ema50": "ema_50", "ema_50": "ema_50",
    "ema100": "ema_100", "ema_100": "ema_100",
    "ema200": "ema_200", "ema_200": "ema_200",

    "sma5": "sma_5", "sma05": "sma_5", "sma_5": "sma_5",
    "sma10": "sma_10", "sma_10": "sma_10",
    "sma20": "sma_20", "sma_20": "sma_20",
    "sma50": "sma_50", "sma_50": "sma_50",
    "sma100": "sma_100", "sma_100": "sma_100",
    "sma200": "sma_200", "sma_200": "sma_200",

    # RSI/ADX/DM+/DM-
    "rsi14": "rsi_14", "rsi_14": "rsi_14",
    "adx14": "adx_14", "adx_14": "adx_14",
    "dmp14": "dmp_14", "dmp_14": "dmp_14",
    "dmn14": "dmn_14", "dmn_14": "dmn_14",

    # Momentum / ROC
    "momentum10": "momentum_10", "momentum_10": "momentum_10",
    "mom10": "momentum_10", "roc10": "roc_10", "roc_10": "roc_10",

    # StochRSI
    "stochrsik": "stochrsi_k", "stochrsi_k": "stochrsi_k",
    "stochrsid": "stochrsi_d", "stochrsi_d": "stochrsi_d",
    "stochrsik141433": "stochrsi_k", "stochrsid141433": "stochrsi_d",

    # Williams %R
    "williamspercentr14": "williams_percent_r_14",
    "williams_percent_r_14": "williams_percent_r_14",
    "williamsr14": "williams_percent_r_14",

    # MACD
    "macd12269": "macd_12_26_9", "macd_12_26_9": "macd_12_26_9",
    "macdsignal12269": "macd_signal_12_26_9",
    "macdhist12269": "macd_hist_12_26_9",
}


# Örüntü temelli genel kurallar (EMA, SMA, RSI, MOM/ROC n, vb.)
_PATTERNS = [
    (re.compile(r"^ema[_\-]?(\d+)$"), lambda m: f"ema_{m.group(1)}"),
    (re.compile(r"^sma[_\-]?(\d+)$"), lambda m: f"sma_{m.group(1)}"),
    (re.compile(r"^rsi[_\-]?(\d+)$"), lambda m: f"rsi_{m.group(1)}"),
    (re.compile(r"^(mom|momentum)[_\-]?(\d+)$"), lambda m: f"momentum_{m.group(2)}"),
    (re.compile(r"^roc[_\-]?(\d+)$"), lambda m: f"roc_{m.group(1)}"),
    (re.compile(r"^adx[_\-]?(\d+)$"), lambda m: f"adx_{m.group(1)}"),
    (re.compile(r"^dmp[_\-]?(\d+)$"), lambda m: f"dmp_{m.group(1)}"),
    (re.compile(r"^dmn[_\-]?(\d+)$"), lambda m: f"dmn_{m.group(1)}"),
]


def canonical_name(name: str) -> str:
    if _MODE == "off":
        return str(name)
    if not isinstance(name, str):
        name = str(name)
    s = _base_norm(name)
    key = _alias_key(s)
    if key in ALIAS:
        return ALIAS[key]
    for pat, fn in _PATTERNS:
        m = pat.match(s)
        if m:
            return fn(m)
    return s  # zaten kanonik


def canonicalize_columns(df):
    if _MODE == "off":
        return df
    df.columns = [canonical_name(c) for c in df.columns]
    return df


def canonicalize_filter_token(token: str) -> str:
    if _MODE == "off":
        return token
    return canonical_name(token)


__all__ = [
    "canonical_name",
    "canonicalize_columns",
    "canonicalize_filter_token",
    "set_name_normalization",
]
