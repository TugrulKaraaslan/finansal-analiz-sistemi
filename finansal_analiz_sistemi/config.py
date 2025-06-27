"""Package level configuration wrapper."""

from importlib import import_module
import sys

_base = import_module("config")

# Expose attributes from base config
ALIM_ZAMANI = getattr(_base, "ALIM_ZAMANI")
TR_HOLIDAYS_REMOVE = getattr(_base, "TR_HOLIDAYS_REMOVE")
OHLCV_MAP = getattr(_base, "OHLCV_MAP")
INDIKATOR_AD_ESLESTIRME = getattr(_base, "INDIKATOR_AD_ESLESTIRME")
SERIES_SERIES_CROSSOVERS = getattr(_base, "SERIES_SERIES_CROSSOVERS")

sys.modules.setdefault("cfg", sys.modules[__name__])
