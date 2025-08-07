# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
import pandas as pd
import pytest

from backtest.indicators import compute_indicators
from backtest.screener import run_screener


def test_compute_indicators_invalid_inputs():
    with pytest.raises(TypeError):
        compute_indicators([])
    df = pd.DataFrame()
    with pytest.raises(TypeError):
        compute_indicators(df, params=[])


def test_run_screener_invalid_inputs():
    filters_df = pd.DataFrame({"FilterCode": [], "PythonQuery": []})
    df_ind = pd.DataFrame(
        {"symbol": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
    )
    with pytest.raises(TypeError):
        run_screener([], filters_df, pd.Timestamp("2024-01-02"))
    with pytest.raises(TypeError):
        run_screener(df_ind, [], pd.Timestamp("2024-01-02"))
    with pytest.raises(ValueError):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    df_ok = df_ind.assign(date=pd.to_datetime([]))
    bad_filters = pd.DataFrame({"FilterCode": []})
    with pytest.raises(ValueError):
        run_screener(df_ok, bad_filters, pd.Timestamp("2024-01-02"))
