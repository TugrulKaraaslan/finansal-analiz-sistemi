import builtins
import types

if getattr(types.SimpleNamespace, "__hash__", None) is None:
    try:
        types.SimpleNamespace.__hash__ = builtins.hash
    except TypeError:
        pass

from hypothesis import settings

settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")
import numpy as np
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
