"""Test module for test_standardize_ohlcv_columns."""

import pandas as pd
import pytest

from finansal_analiz_sistemi.data_loader import _standardize_ohlcv_columns


@pytest.mark.parametrize(
    "raw_columns, expected_columns",
    [
        (
            {
                "Açılış": [1],
                "Yüksek": [2],
                "Düşük": [0],
                "Kapanış": [1],
                "Miktar": [10],
            },
            {"open", "high", "low", "close", "volume"},
        ),
        (
            {
                "OPEN": [1],
                "HIGH": [2],
                "LOW": [0],
                "CLOSE": [1],
                "VOLUME": [10],
            },
            {"open", "high", "low", "close", "volume"},
        ),
    ],
)
def test_standardize_ohlcv_columns(raw_columns, expected_columns):
    """Test test_standardize_ohlcv_columns."""
    df = pd.DataFrame(raw_columns)
    standardized_df = _standardize_ohlcv_columns(df, "dummy")
    assert expected_columns.issubset(set(standardized_df.columns))
