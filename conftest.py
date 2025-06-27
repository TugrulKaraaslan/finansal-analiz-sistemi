import types

import numpy as np
import pandas as pd
import pytest

# Hypothesis scans sys.modules during test collection.  Our tests inject
# ``types.SimpleNamespace`` objects as stubs, but these are not hashable by
# default, which leads to ``TypeError`` when Hypothesis tries to create a set
# from module values.  Provide a simple ``__hash__`` implementation early so
# that test collection succeeds regardless of import order.
if not hasattr(types.SimpleNamespace, "__hash__"):
    types.SimpleNamespace.__hash__ = lambda self: id(self)


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
