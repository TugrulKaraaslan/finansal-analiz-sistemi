import pandas as pd
import pytest

from backtest.query_parser import SafeQuery
from backtest.screener import run_screener


def test_safequery_basic():
    q = SafeQuery("rsi_14 > 70 & close>ema_20")
    assert q.is_safe


def test_safequery_supports_not_operator():
    df = pd.DataFrame({"close": [1, -1]})
    q = SafeQuery("not (close > 0)")
    assert q.is_safe
    out = q.filter(df)
    assert out["close"].tolist() == [-1]


def test_safequery_rejects_calls_and_attributes():
    assert not SafeQuery("__import__('os').system('echo 1')").is_safe
    assert not SafeQuery("df.__class__").is_safe


def test_run_screener_skips_unsafe(caplog):
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
    filters = pd.DataFrame(
        {
            "FilterCode": ["SAFE", "BAD"],
            "PythonQuery": ["close > 0", "__import__('os').system('echo 1')"],
        }
    )
    logger.add(caplog.handler, level="WARNING")
    res = run_screener(
        df_ind,
        filters,
        pd.Timestamp("2024-01-02"),
        stop_on_filter_error=False,
    )
    assert res["FilterCode"].tolist() == ["SAFE"]
    assert isinstance(res.loc[0, "Date"], pd.Timestamp)
    assert "unsafe expression" in caplog.text


def test_run_screener_missing_columns_raises():
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
    filters = pd.DataFrame(
        {
            "FilterCode": ["GOOD", "BAD"],
            "PythonQuery": ["close > 0", "nonexistent > 0"],
        }
    )
    with pytest.raises(ValueError):
        run_screener(
            df_ind,
            filters,
            pd.Timestamp("2024-01-02"),
            stop_on_filter_error=True,
        )


def test_run_screener_skips_missing_columns_relaxed(caplog):
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
    filters = pd.DataFrame(
        {
            "FilterCode": ["GOOD", "BAD"],
            "PythonQuery": ["close > 0", "nonexistent > 0"],
        }
    )
    logger.add(caplog.handler, level="WARNING")
    res = run_screener(
        df_ind,
        filters,
        pd.Timestamp("2024-01-02"),
        stop_on_filter_error=False,
    )
    assert res["FilterCode"].tolist() == ["GOOD"]
    assert isinstance(res.loc[0, "Date"], pd.Timestamp)
    assert "skip filter: missing column" in caplog.text


def test_run_screener_raises_on_filter_error_default():
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
    filters = pd.DataFrame(
        {
            "FilterCode": ["BAD"],
            "PythonQuery": ["CROSSUP(close, 'a')"],
        }
    )
    with pytest.raises(RuntimeError):
        run_screener(df_ind, filters, pd.Timestamp("2024-01-02"))


def test_run_screener_warns_on_filter_error_disabled():
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
    filters = pd.DataFrame(
        {
            "FilterCode": ["GOOD", "BAD"],
            "PythonQuery": ["close > 0", "CROSSUP(close, 'a')"],
        }
    )
    with pytest.warns(UserWarning) as w:
        res = run_screener(
            df_ind,
            filters,
            pd.Timestamp("2024-01-02"),
            raise_on_error=False,
        )
    assert res["FilterCode"].tolist() == ["GOOD"]
    assert isinstance(res.loc[0, "Date"], pd.Timestamp)
    assert any("BAD" in str(msg.message) for msg in w)


def test_safequery_allows_whitelist_functions():
    df = pd.DataFrame({"x": [1, 2, 3]})
    q = SafeQuery("x.notna() and x.isin([1,2])")
    assert q.is_safe
    out = q.filter(df)
    assert out["x"].tolist() == [1, 2]


def test_safequery_allows_strings_and_methods():
    df = pd.DataFrame({"symbol": ["AAA", "BBB"], "close": [1, 2]})
    q = SafeQuery("symbol == 'AAA' & close.abs() > 0")
    assert q.is_safe
    out = q.filter(df)
    assert out["symbol"].tolist() == ["AAA"]


def test_safequery_allows_str_contains():
    df = pd.DataFrame({"symbol": ["AAA", "BBB"]})
    q = SafeQuery("symbol.str.contains('A')")
    assert q.is_safe
    out = q.filter(df)
    assert out["symbol"].tolist() == ["AAA"]


def test_safequery_allows_extra_funcs():
    df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
    q = SafeQuery("x.rolling(2).max() >= 2")
    assert q.is_safe
    assert not q.filter(df).empty
    q2 = SafeQuery("x.rolling(2).std() >= 0")
    assert q2.is_safe
    assert not q2.filter(df).empty
    q3 = SafeQuery("x.rolling(2).median() >= 1")
    assert q3.is_safe
    assert not q3.filter(df).empty


def test_safequery_allows_math_funcs():
    df = pd.DataFrame({"x": [1.0, 2.0, 3.0]})
    q = SafeQuery("log(x) >= 0 & exp(x) > 0 & floor(x) >= 1 & ceil(x) <= 4")
    assert q.is_safe
    out = q.filter(df)
    assert out["x"].tolist() == [1.0, 2.0, 3.0]


def test_safequery_allows_cross_up():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    q = SafeQuery("CROSSUP(a, b)")
    assert q.is_safe
    mask = q.get_mask(df)
    assert mask.tolist() == [False, False, True]


def test_filter_parser_normalization():
    q = SafeQuery("EMA20 > Close")
    assert q.names == {"ema_20", "close"}
