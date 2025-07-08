"""Test module for test_dtypes_ok."""

import numpy as np
import pandas as pd

from finansal.utils import safe_set
from finansal_analiz_sistemi import config


def test_safe_set_casts_to_config_dtype():
    """Test test_safe_set_casts_to_config_dtype."""
    df = pd.DataFrame({"adx_14": pd.Series([1, 2], dtype="int64")})
    safe_set(df, "adx_14", np.array([1.5, 2.5]))
    assert df["adx_14"].dtype == config.DTYPES_MAP["adx_14"]


def test_safe_set_keeps_index_alignment():
    """Test test_safe_set_keeps_index_alignment."""
    df = pd.DataFrame({"close": [10, 20]}, index=[5, 6])
    safe_set(df, "ema_10", [1, 2])
    assert list(df.index) == [5, 6]
    assert df.loc[5, "ema_10"] == 1


def test_safe_set_fallback_dtype():
    """Test test_safe_set_fallback_dtype."""
    df = pd.DataFrame({"volume": pd.Series([1, 2], dtype="int32")})
    safe_set(df, "volume", [1, np.nan])
    assert df["volume"].dtype == "float32"
