"""Global yapılandırma sabitleri."""

import sys
from pathlib import Path

# Flag to indicate the application is running in Google Colab
IS_COLAB: bool = False

CACHE_PATH: Path = Path("veri/birlesik_hisse_verileri.parquet")
DEFAULT_CSV_PATH: Path = Path("data/raw/all_prices.csv")

# dtype downcast mappings for CSV reading
DTYPES: dict[str, str] = {
    "open": "float32",
    "high": "float32",
    "low": "float32",
    "close": "float32",
    "volume": "int32",
}

# final dataframe dtypes
DTYPES_MAP: dict[str, str] = {
    "open": "float32",
    "high": "float32",
    "low": "float32",
    "close": "float32",
    "volume": "int32",
    # common indicators
    "rsi_14": "float32",
    "macd": "float32",
    "ema_10": "float32",
    "ema_20": "float32",
    "sma_20": "float32",
    "adx_14": "float32",
}

# chunk size for indicator calculation
CHUNK_SIZE: int = 1

# ---------------------------------------------------------------------------
# Optional defaults
if "ALIM_ZAMANI" not in globals():
    ALIM_ZAMANI = "open"

if "TR_HOLIDAYS_REMOVE" not in globals():
    TR_HOLIDAYS_REMOVE = False

if "OHLCV_MAP" not in globals():
    OHLCV_MAP = {
        "Açılış": "open",
        "OPEN": "open",
        "Yüksek": "high",
        "HIGH": "high",
        "Düşük": "low",
        "LOW": "low",
        "Kapanış": "close",
        "CLOSE": "close",
        "Miktar": "volume",
        "VOLUME": "volume",
    }

if "INDIKATOR_AD_ESLESTIRME" not in globals():
    INDIKATOR_AD_ESLESTIRME: dict = {}

if "SERIES_SERIES_CROSSOVERS" not in globals():
    SERIES_SERIES_CROSSOVERS: list = []

sys.modules.setdefault("cfg", sys.modules[__name__])

if not hasattr(sys.modules[__name__], "SATIS_ZAMANI"):
    SATIS_ZAMANI = globals().get("ALIM_ZAMANI", "close")

if not hasattr(sys.modules[__name__], "SERIES_VALUE_CROSSOVERS"):
    SERIES_VALUE_CROSSOVERS: list = []

if not hasattr(sys.modules[__name__], "cfg"):
    cfg = sys.modules[__name__]

import sys  # noqa: E402

if not hasattr(sys.modules[__name__], "KOMISYON_ORANI"):
    KOMISYON_ORANI = 0.001
if not hasattr(sys.modules[__name__], "TA_STRATEGY"):
    TA_STRATEGY: dict = {}
if not hasattr(sys.modules[__name__], "get"):

    def get(key, default=None):
        return globals().get(key, default)


# ---------------------------------------------------------------------------
# Defaults for passive filters and custom column parameters
import sys

if not hasattr(sys.modules[__name__], "passive_filters"):
    passive_filters = ["T31"]
if not hasattr(sys.modules[__name__], "OZEL_SUTUN_PARAMS"):
    OZEL_SUTUN_PARAMS = {}
