import pandas as pd
import pytest

from finansal_analiz_sistemi.data_loader import data_loader_standardize_ohlcv_columns

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
                "Open": [1],
                "High": [2],
                "Low": [0],
                "Close": [1],
                "Volume": [10],
            },
            {"open", "high", "low", "close", "volume"},
        ),
    ],
)
def test_standardize_ohlcv_columns(raw_columns, expected_columns):
    df = pd.DataFrame(raw_columns)
    standardized_df = data_loader_standardize_ohlcv_columns(df, "dummy")
    assert expected_columns.issubset(set(standardized_df.columns))
