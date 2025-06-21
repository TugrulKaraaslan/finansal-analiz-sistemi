import pandas as pd
import numpy as np
import pytest

from utils.pandas_option_safe import ensure_option

ensure_option("future.no_silent_downcasting", True)


@pytest.fixture
def sample_filtreler():
    return pd.DataFrame(
        {
            "kod": ["T0", "T1"],
            "PythonQuery": ["close > 0", "volume > 0"],
        }
    )


@pytest.fixture
def sample_indikator_df():
    return pd.DataFrame({"close": [10, 11], "relative_volume": [1.2, 1.3]})


@pytest.fixture
def big_df():
    """Large DataFrame fixture around 100 MB in memory."""
    n = 90_000
    return pd.DataFrame(
        {
            "tarih": pd.date_range("2025-01-01", periods=n, freq="B"),
            "close": np.random.rand(n) * 100,
            "open": np.random.rand(n) * 100,
            "high": np.random.rand(n) * 100,
            "low": np.random.rand(n) * 100,
            "volume": np.random.randint(1_000_000, 10_000_000, n),
        }
    )
