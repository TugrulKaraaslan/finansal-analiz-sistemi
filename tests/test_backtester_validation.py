# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
import pandas as pd
import pytest

from backtest.backtester import run_1g_returns


def _base_df():
    return pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]).normalize(),
            "close": [1.0, 1.1],
            "next_date": pd.to_datetime(["2024-01-02", "2024-01-03"]).normalize(),
            "next_close": [1.1, 1.2],
        }
    )


def _signals_df():
    return pd.DataFrame(
        {
            "FilterCode": ["F"],
            "Symbol": ["AAA"],
            "Date": pd.to_datetime(["2024-01-01"]).normalize(),
        }
    )


def test_run_1g_returns_type_validation():
    with pytest.raises(TypeError):
        run_1g_returns([], pd.DataFrame())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        run_1g_returns(_base_df(), [])  # type: ignore[arg-type]


def test_run_1g_returns_missing_columns():
    bad_df = pd.DataFrame({"symbol": ["AAA"]})
    with pytest.raises(ValueError):
        run_1g_returns(bad_df, _signals_df())
    bad_sig = pd.DataFrame({"FilterCode": ["F"], "Symbol": ["AAA"]})
    with pytest.raises(ValueError):
        run_1g_returns(_base_df(), bad_sig)


def test_run_1g_returns_empty_signals():
    out = run_1g_returns(
        _base_df(), pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    )
    assert out.empty


def test_run_1g_returns_logs_empty_signals(caplog):
    from loguru import logger

    logger.add(caplog.handler, level="WARNING")
    out = run_1g_returns(
        _base_df(), pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    )
    assert out.empty
    assert "signals DataFrame is empty" in caplog.text


def test_run_1g_returns_logs_missing_base_columns(caplog):
    from loguru import logger

    bad_df = _base_df().drop(columns=["close"])
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_1g_returns(bad_df, _signals_df())
    assert caplog.records[0].levelname == "ERROR"
    assert "Eksik kolon(lar): close" in caplog.text


def test_run_1g_returns_logs_missing_signal_columns(caplog):
    from loguru import logger

    bad_sig = _signals_df().drop(columns=["Date"])
    logger.add(caplog.handler, level="ERROR")
    with pytest.raises(ValueError):
        run_1g_returns(_base_df(), bad_sig)
    assert caplog.records[0].levelname == "ERROR"
    assert "Eksik kolon(lar): Date" in caplog.text
