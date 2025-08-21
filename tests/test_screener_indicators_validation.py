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
        {"symbol": [], "open": [], "high": [],
            "low": [], "close": [], "volume": []}
    )
    with pytest.raises(TypeError):
        run_screener([], filters_df, pd.Timestamp("2024-01-02"))
    with pytest.raises(TypeError):
        run_screener(df_ind, [], pd.Timestamp("2024-01-02"))
    with pytest.raises(ValueError):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    df_ok = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    bad_filters = pd.DataFrame({"FilterCode": []})
    with pytest.raises(ValueError):
        run_screener(df_ok, bad_filters, pd.Timestamp("2024-01-02"))


def test_run_screener_empty_dataset_logs(caplog):
    from loguru import logger

    df_empty = pd.DataFrame(
        columns=["symbol", "date", "open", "high", "low", "close", "volume"]
    )
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close > 1"]})
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_screener(df_empty, filters_df, pd.Timestamp("2024-01-02"))
    assert "df_ind is empty" in caplog.text


def test_run_screener_empty_filters_logs(caplog):
    from loguru import logger

    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(columns=["FilterCode", "PythonQuery"])
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert "filters_df is empty" in caplog.text


def test_run_screener_logs_missing_df_columns(caplog):
    from loguru import logger

    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close > 1"]})
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert caplog.records[0].levelname == "ERROR"
    assert "df_ind missing columns: close" in caplog.text


def test_run_screener_logs_missing_filters_columns(caplog):
    from loguru import logger

    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame({"FilterCode": ["F1"]})
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert caplog.records[0].levelname == "ERROR"
    assert "filters_df missing required columns" in caplog.text


def test_run_screener_outputs_timestamp_dates():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close > 0"]})
    res = run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert isinstance(res.loc[0, "Date"], pd.Timestamp)


def test_run_screener_side_validation():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(
        {
            "FilterCode": ["F1"],
            "PythonQuery": ["close > 0"],
            "Side": ["long"],
        }
    )
    res = run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
    assert res.loc[0, "Side"] == "long"
    bad = filters_df.copy()
    bad["Side"] = ["foo"]
    with pytest.raises(ValueError):
        run_screener(
            df_ind,
            bad,
            pd.Timestamp("2024-01-02"),
            stop_on_filter_error=True,
        )


def test_run_screener_duplicate_filter_code():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).normalize(),
            "open": [1.0],
            "high": [1.0],
            "low": [1.0],
            "close": [1.0],
            "volume": [100],
        }
    )
    filters_df = pd.DataFrame(
        {
            "FilterCode": ["F1", "F1"],
            "PythonQuery": ["close > 0", "close > 1"],
        }
    )
    with pytest.raises(ValueError, match="Duplicate FilterCode"):
        run_screener(df_ind, filters_df, pd.Timestamp("2024-01-02"))
