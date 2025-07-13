"""Global configuration constants for the analysis system.

These values are loaded from ``config.yml`` when present and define default
paths, indicator lists and runtime settings used throughout the package.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

import sys  # isort: skip


def get_settings_path(custom: str | None = None) -> Path:
    """Return the absolute path to ``settings.yaml``.

    Args:
        custom (str | None): Optional user-provided settings file path.

    Returns:
        Path: Resolved path to ``settings.yaml``.

    """
    if custom:
        return Path(custom).expanduser().resolve()
    env_path = os.getenv("FAS_SETTINGS_FILE")
    if env_path:
        return Path(env_path).expanduser().resolve()
    is_colab = "google.colab" in sys.modules or bool(os.getenv("COLAB_GPU"))
    if is_colab:
        return Path("/content/drive/MyDrive/finansal-analiz-sistemi/settings.yaml")
    return Path(__file__).resolve().parent.parent / "settings.yaml"


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

# Final DataFrame dtypes
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
        "IKS_26": "ichimoku_baseline",
        "ISA_9": "ichimoku_leadingspana",
        "ISB_26": "ichimoku_leadingspanb",
    }
else:
    INDIKATOR_AD_ESLESTIRME.setdefault("ITS_9", "ichimoku_conversionline")
    INDIKATOR_AD_ESLESTIRME.setdefault("its_9", "ichimoku_conversionline")
    INDIKATOR_AD_ESLESTIRME.setdefault("IKS_26", "ichimoku_baseline")
    INDIKATOR_AD_ESLESTIRME.setdefault("ISA_9", "ichimoku_leadingspana")
    INDIKATOR_AD_ESLESTIRME.setdefault("ISB_26", "ichimoku_leadingspanb")

if "SERIES_SERIES_CROSSOVERS" not in globals():
    SERIES_SERIES_CROSSOVERS: list = [
        (
            "close",
            "classicpivots_1h_p",
            "close_keser_classicpivots_1h_p_yukari",
            "close_keser_classicpivots_1h_p_asagi",
        )
    ]

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
    TA_STRATEGY: dict = {
        "name": "core",
        "ta": [
            {
                "kind": "rsi",
                "length": 14,
                "col_names": ["rsi_14"],
            },
            {
                "kind": "macd",
                "fast": 12,
                "slow": 26,
                "signal": 9,
                "col_names": ["macd_line", "macd_signal", "macd_hist"],
            },
            {
                "kind": "stochrsi",
                "length": 14,
                "col_names": ["stochrsi_k", "stochrsi_d"],
            },
            {
                "kind": "ichimoku",
                "tenkan": 9,
                "kijun": 26,
                "senkou": 52,
                "col_names": [
                    "ichimoku_leadingspana",
                    "ichimoku_leadingspanb",
                    "ITS_9",
                    "IKS_26",
                    "ICS_26",
                ],
            },
        ],
    }
if not hasattr(sys.modules[__name__], "get"):

    def get(key, default=None):
        """Return a configuration variable or a default value.

        Args:
            key (str): Name of the configuration variable.
            default (Any, optional): Value to return if ``key`` is missing.

        Returns:
            Any: Configuration value or ``default`` if not set.

        """
        return globals().get(key, default)


if not hasattr(sys.modules[__name__], "passive_filters"):
    passive_filters = ["T31"]
if not hasattr(sys.modules[__name__], "filter_weights"):
    filter_weights: dict = {}
if not hasattr(sys.modules[__name__], "OZEL_SUTUN_PARAMS"):
    OZEL_SUTUN_PARAMS: list[dict] = [
        {"name": "classicpivots_1h_p", "function": "_calculate_classicpivots_1h_p"}
    ]

# ---------------------------------------------------------------------------
# Teknik analizde zorunlu olarak üretilecek hareketli ortalamalar
# ---------------------------------------------------------------------------

from typing import List  # noqa: E402

# Basit/üstel vb. MA hesaplamalarında gereken pencere uzunlukları
GEREKLI_MA_PERIYOTLAR: List[int] = [5, 8, 20, 50, 100, 200]
