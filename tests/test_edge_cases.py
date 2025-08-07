# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
import pandas as pd
import pytest

from backtest.normalizer import normalize
from backtest.screener import run_screener
from backtest.validator import quality_warnings


def test_normalize_type_and_missing_columns():
    with pytest.raises(TypeError):
        normalize([])  # not a DataFrame
    df_missing = pd.DataFrame({"symbol": ["AAA"], "close": [1.0]})
    with pytest.raises(ValueError):
        normalize(df_missing)


def test_quality_warnings_no_issues():
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]).date,
            "close": [1.0, 2.0],
        }
    )
    res = quality_warnings(df)
    assert list(res.columns) == ["symbol", "date", "issue", "value"]
    assert res.empty


def test_run_screener_no_hits():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).date,
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )  # TİP DÜZELTİLDİ
    filters_df = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 2"]})
    res = run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert list(res.columns) == ["FilterCode", "Symbol", "Date"]
    assert res.empty
