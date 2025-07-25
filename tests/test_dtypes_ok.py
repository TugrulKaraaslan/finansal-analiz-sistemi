"""Tests validating configured column dtypes.

``safe_set`` should always cast arrays to the dtypes specified in the
configuration so that downstream operations remain consistent.
"""

import numpy as np
import pandas as pd

from finansal.utils import safe_set
from finansal_analiz_sistemi import config


def test_safe_set_casts_to_config_dtype():
    """Ensure ``safe_set`` casts arrays to configured dtypes."""
    df = pd.DataFrame({"adx_14": pd.Series([1, 2], dtype="int64")})
    safe_set(df, "adx_14", np.array([1.5, 2.5]))
    assert df["adx_14"].dtype == config.DTYPES_MAP["adx_14"]


def test_safe_set_keeps_index_alignment():
    """Assignment must preserve the DataFrame index order."""
    df = pd.DataFrame({"close": [10, 20]}, index=[5, 6])
    safe_set(df, "ema_10", [1, 2])
    assert list(df.index) == [5, 6]
    assert df.loc[5, "ema_10"] == 1


def test_safe_set_fallback_dtype():
    """Fallback to float dtype when ``NaN`` values are present."""
    df = pd.DataFrame({"volume": pd.Series([1, 2], dtype="int32")})
    safe_set(df, "volume", [1, np.nan])
    assert str(df["volume"].dtype) == "Int32"


def test_safe_set_handles_length_mismatch():
    """Input shorter than DataFrame length should be reindexed with NaN."""
    df = pd.DataFrame({"close": [10, 20, 30]})
    # Provide only two values for three rows
    safe_set(df, "ema_5", [1, 2])
    assert list(df["ema_5"][:2]) == [1, 2]
    assert pd.isna(df["ema_5"].iloc[2])


def test_safe_set_series_input_reindexes():
    """Series input should be reindexed to match the DataFrame index."""
    df = pd.DataFrame({"close": [10, 20]}, index=[5, 6])
    series = pd.Series([1, 2], index=[6, 5])
    safe_set(df, "ema_10", series)
    assert list(df["ema_10"]) == [2, 1]
