"""Package level configuration wrapper."""

import sys
from importlib import import_module

_base = import_module("config")

# Expose attributes from base config
ALIM_ZAMANI = getattr(_base, "ALIM_ZAMANI")
TR_HOLIDAYS_REMOVE = getattr(_base, "TR_HOLIDAYS_REMOVE")
OHLCV_MAP = getattr(_base, "OHLCV_MAP")
INDIKATOR_AD_ESLESTIRME = getattr(_base, "INDIKATOR_AD_ESLESTIRME")
SERIES_SERIES_CROSSOVERS = getattr(_base, "SERIES_SERIES_CROSSOVERS")
IS_COLAB = getattr(_base, "IS_COLAB")

sys.modules.setdefault("cfg", sys.modules[__name__])

# ---------------------------------------------------------------------------
# TEST FALLBACKS
# ---------------------------------------------------------------------------

# SATIS_ZAMANI default
SATIS_ZAMANI = globals().get("SATIS_ZAMANI", "close")

# Empty default for value crossovers
SERIES_VALUE_CROSSOVERS = globals().get("SERIES_VALUE_CROSSOVERS", [])

# Ensure Ichimoku alias exists
INDIKATOR_AD_ESLESTIRME = globals().get("INDIKATOR_AD_ESLESTIRME", {})
INDIKATOR_AD_ESLESTIRME.setdefault("its_9", "ichimoku_conversionline")

# Legacy `cfg` alias
cfg = sys.modules.setdefault("cfg", sys.modules[__name__])

# default chunk size for indicator calculations
CHUNK_SIZE: int = 1
# Minimal gösterge listesi – back-test'in başlatılması için gerekli
CORE_INDICATORS = [
    "ema_10",
    "ema_20",
    "rsi_14",
    "macd",
]
