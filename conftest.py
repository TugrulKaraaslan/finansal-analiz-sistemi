"""Pytest ortak yardımcıları ve Hypothesis ayarları.

* Hypothesis < 6.101 sürümlerinde `types.SimpleNamespace`
  üzerinde `__hash__` tanımlı değildir. Aşağıdaki shim,
  eski ortamlarda bu hatayı engeller.
"""

from __future__ import annotations

import builtins
import types

import numpy as np
import pandas as pd
import pytest
from hypothesis import settings

# ───────────────────────────────────────────────
# G-5 Shim – SimpleNamespace hash problemi
# ───────────────────────────────────────────────
if getattr(types.SimpleNamespace, "__hash__", None) is None:
    try:
        types.SimpleNamespace.__hash__ = builtins.hash  # type: ignore[attr-defined]
    except TypeError:
        pass
# CI profilini yükle (daha hızlı test)
# ───────────────────────────────────────────────
# Ortak pytest fixture’ları
# ───────────────────────────────────────────────
def dummy_df() -> pd.DataFrame:
    """Küçük sahte OHLCV verisi (10 satır) döndürür."""
    rows = 10
            "volume": np.random.randint(1_000, 10_000, rows),


# -----------------------------------------------------------------------------
import pandas as pd
import pytest


@pytest.fixture
def big_df() -> pd.DataFrame:
    rows = 10_000
    return pd.DataFrame(
        {
            "hisse_kodu": ["AAA"] * rows,
            "tarih": pd.date_range("2024-01-01", periods=rows, freq="T"),
            "open": np.random.rand(rows),
            "high": np.random.rand(rows),
            "low": np.random.rand(rows),
            "close": np.random.rand(rows),
            "volume": np.random.randint(1, 1000, rows),
        }
    )
