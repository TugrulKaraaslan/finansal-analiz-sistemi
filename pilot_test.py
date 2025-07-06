import importlib
import importlib.metadata
import sys
import time

import numpy as np
import pandas as pd

# Monkey patch numpy for legacy pandas_ta
if not hasattr(np, "NaN"):
    np.NaN = np.nan

# import legacy pandas_ta
import pandas_ta as ta_legacy

# remove pandas_ta modules to import openbb version in isolation
legacy_modules = {
    name: mod for name, mod in sys.modules.items() if name.startswith("pandas_ta")
}
for name in list(sys.modules):
    if name.startswith("pandas_ta"):
        del sys.modules[name]

# ensure importlib.metadata attribute exists as expected
setattr(importlib, "metadata", importlib.metadata)

# import openbb pandas_ta from preinstalled path
sys.path.insert(0, "/tmp/openbb_pkg")
ta_openbb = importlib.import_module("pandas_ta")
sys.path.pop(0)

# restore legacy module reference for convenience
sys.modules["pandas_ta_legacy"] = ta_legacy
sys.modules["pandas_ta_openbb"] = ta_openbb

# Load sample data
DF = pd.read_csv("sample_OHLC.csv")

# Helper to compute indicators using a pandas_ta module


def compute(mod):
    start = time.perf_counter()
    rsi = mod.rsi(DF["close"], length=14)
    sma = mod.sma(DF["close"], length=20)
    macd = mod.macd(DF["close"], fast=12, slow=26, signal=9)
    dur = time.perf_counter() - start
    return rsi, sma, macd, dur


rsi_legacy, sma_legacy, macd_legacy, t_legacy = compute(ta_legacy)
rsi_openbb, sma_openbb, macd_openbb, t_openbb = compute(ta_openbb)

# Drop warmup period for comparison
trim = 26

assert np.allclose(rsi_legacy[trim:], rsi_openbb[trim:], atol=1e-12, equal_nan=True)
assert np.allclose(sma_legacy[trim:], sma_openbb[trim:], atol=1e-12, equal_nan=True)
assert np.allclose(macd_legacy[trim:], macd_openbb[trim:], atol=1e-12, equal_nan=True)

print(f"Legacy pandas_ta time: {t_legacy:.6f}s")
print(f"OpenBB pandas_ta time: {t_openbb:.6f}s")
