"""Package level configuration wrapper."""

import sys
import sys as _sys
from importlib import import_module

_base = import_module("config")

# Expose attributes from base config
ALIM_ZAMANI = getattr(_base, "ALIM_ZAMANI")
TR_HOLIDAYS_REMOVE = getattr(_base, "TR_HOLIDAYS_REMOVE")
OHLCV_MAP = getattr(_base, "OHLCV_MAP")
INDIKATOR_AD_ESLESTIRME = getattr(_base, "INDIKATOR_AD_ESLESTIRME")
SERIES_SERIES_CROSSOVERS = getattr(_base, "SERIES_SERIES_CROSSOVERS")

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

# Environment flag
IS_COLAB = globals().get("IS_COLAB", False)

# Ensure the attribute exists for downstream imports
if "IS_COLAB" not in globals():
    IS_COLAB = False

# Legacy `cfg` alias
cfg = _sys.modules.setdefault("cfg", _sys.modules[__name__])
