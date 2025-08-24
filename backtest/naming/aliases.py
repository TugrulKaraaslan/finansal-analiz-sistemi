from __future__ import annotations

import re

# 1) Düz alias haritası (tekilleştirme)
ALIAS_MAP: dict[str, str] = {
    # temel OHLCV
    "tarih": "date",
    "date": "date",
    "kapanis": "close",
    "close": "close",
    "acilis": "open",
    "open": "open",
    "yuksek": "high",
    "high": "high",
    "dusuk": "low",
    "low": "low",
    "hacim": "volume",
    "islem_hacmi": "volume",
    "lot": "volume",
    "volume": "volume",
}

# 2) Desen bazlı alias (parametreli göstergeler)
PATTERN_ALIASES: list[tuple[re.Pattern[str], str]] = [
    # SMA/EMA/RSI
    (re.compile(r"^(sma)(\d+)$", re.I), r"sma_\2"),
    (re.compile(r"^(ema)(\d+)$", re.I), r"ema_\2"),
    (re.compile(r"^(rsi)(\d+)$", re.I), r"rsi_\2"),
    # MACD varyantları (macd_12_26_9 parçaları)
    (re.compile(r"^(macd[_-]?line)$", re.I), "macd_line"),
    (re.compile(r"^(macd[_-]?signal)$", re.I), "macd_signal"),
    # Bollinger (BBU/BBM/BBL) — parametreler: period, dev
    (re.compile(r"^(bbu|bbupper)[_-]?(\d+)[_.]?(\d+(?:p\d+)?)$", re.I), r"bbu_\2_\3"),
    (re.compile(r"^(bbm|bbmid)[_-]?(\d+)[_.]?(\d+(?:p\d+)?)$", re.I), r"bbm_\2_\3"),
    (re.compile(r"^(bbl|bblower)[_-]?(\d+)[_.]?(\d+(?:p\d+)?)$", re.I), r"bbl_\2_\3"),
    # ADX/DI
    (re.compile(r"^(adx)[_-]?(\d+)$", re.I), r"adx_\2"),
    (re.compile(r"^\+di[_-]?(\d+)$", re.I), r"plus_di_\1"),
    (re.compile(r"^-di[_-]?(\d+)$", re.I), r"minus_di_\1"),
]

_DECIMAL = re.compile(r"(?<=_)\d+\.\d+(?=(_|\b))")  # alt çizgiden sonra gelen ondalık parametreler
_WS = re.compile(r"\s+")
_DASH = re.compile(r"[-]+")
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


def _decimals_to_p(s: str) -> str:
    # alt çizgi ile ayrılmış parametrelerde 20.5 -> 20p5, 2.0 -> 2
    s = _DECIMAL.sub(lambda m: m.group(0).replace(".", "p"), s)
    return s.replace("p0", "")


def normalize_token(name: str) -> str:
    """Return the canonical ``snake_case`` form of *name*."""

    if not name:
        return name
    s = name.strip().translate(_TURK)
    s = _WS.sub("_", s)
    s = _DASH.sub("_", s)
    s = s.replace("__", "_")
    s = s.lower()
    if s in ALIAS_MAP:
        s = ALIAS_MAP[s]
    for pat, repl in PATTERN_ALIASES:
        if pat.match(s):
            s = pat.sub(repl, s)
            break
    s = _decimals_to_p(s)
    return s
