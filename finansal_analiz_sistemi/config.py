"""Global yapılandırma sabitleri."""

import sys  # isort: skip
from pathlib import Path

import yaml

# Flag to indicate the application is running in Google Colab
IS_COLAB: bool = False

# Project root path so config can resolve files from any CWD
BASE_DIR: Path = Path(__file__).resolve().parents[1]

# unified Parquet cache location relative to project root
PARQUET_CACHE_PATH: str = "veri/birlesik_hisse_verileri.parquet"
CACHE_PATH: Path = BASE_DIR / PARQUET_CACHE_PATH
DEFAULT_CSV_PATH: Path = BASE_DIR / "data" / "raw" / "all_prices.csv"

# default data directory and filename patterns
# Use real data directory by default
VERI_KLASORU: Path = BASE_DIR / "veri"
HISSE_DOSYA_PATTERN: str = str(VERI_KLASORU / "*.csv")
PARQUET_ANA_DOSYA_YOLU: Path = CACHE_PATH

# default filter rules CSV path
FILTRE_DOSYA_YOLU: Path = BASE_DIR / "veri" / "15.csv"

# Load optional configuration overrides from 'config.yml'
_CFG_FILE = BASE_DIR / "config.yml"
if _CFG_FILE.exists():
    with _CFG_FILE.open() as f:
        _CFG = yaml.safe_load(f) or {}
        globals().update(_CFG)
else:
    _CFG = {}

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

# minimal indicator subset used for smoke tests and CLI defaults
# This example list can be overridden in 'config.yml' if needed
CORE_INDICATORS: list[str] = [
    "ema_10",
    "ema_20",
    "rsi_14",
    "macd",
]

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
    INDIKATOR_AD_ESLESTIRME: dict = {
        "ITS_9": "ichimoku_conversionline",
        "its_9": "ichimoku_conversionline",
    }
else:
    INDIKATOR_AD_ESLESTIRME.setdefault("ITS_9", "ichimoku_conversionline")
    INDIKATOR_AD_ESLESTIRME.setdefault("its_9", "ichimoku_conversionline")

if "SERIES_SERIES_CROSSOVERS" not in globals():
    SERIES_SERIES_CROSSOVERS: list = []

sys.modules.setdefault("cfg", sys.modules[__name__])

if not hasattr(sys.modules[__name__], "SATIS_ZAMANI"):
    SATIS_ZAMANI = globals().get("ALIM_ZAMANI", "close")

if not hasattr(sys.modules[__name__], "SERIES_VALUE_CROSSOVERS"):
    SERIES_VALUE_CROSSOVERS: list = []

if not hasattr(sys.modules[__name__], "cfg"):
    cfg = sys.modules[__name__]

if not hasattr(sys.modules[__name__], "KOMISYON_ORANI"):
    KOMISYON_ORANI = 0.001
if not hasattr(sys.modules[__name__], "TA_STRATEGY"):
    TA_STRATEGY: dict = {}
if not hasattr(sys.modules[__name__], "get"):

    def get(key, default=None):
        return globals().get(key, default)


if not hasattr(sys.modules[__name__], "passive_filters"):
    passive_filters = ["T31"]  # D2
if not hasattr(sys.modules[__name__], "filter_weights"):
    filter_weights: dict = {}
if not hasattr(sys.modules[__name__], "OZEL_SUTUN_PARAMS"):
    OZEL_SUTUN_PARAMS: dict = {}  # D3

# ---------------------------------------------------------------------------
# Teknik analizde zorunlu olarak üretilecek hareketli ortalamalar
# ---------------------------------------------------------------------------

from typing import List  # noqa: E402

# Basit/üstel vb. MA hesaplamalarında gereken pencere uzunlukları
GEREKLI_MA_PERIYOTLAR: List[int] = [5, 8, 20, 50, 100, 200]
