import pandas as pd

from backtest.indicators import compute_indicators


def _sample_df():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    return pd.DataFrame(
        {
            "symbol": ["AAA"] * 30,
            "date": dates,
            "close": range(1, 31),
            "volume": range(1, 31),
        }
    )


def test_macd_disabled():
    df = _sample_df()
    res = compute_indicators(df, params={"macd": []}, engine="builtin")
    assert not any(col.startswith("MACD") for col in res.columns)


def test_builtin_engine_basic():
    df = _sample_df()
    res = compute_indicators(df, params={}, engine="builtin")
    assert "EMA_10" in res.columns
    assert "RSI_14" in res.columns


def test_pandas_ta_fallback(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pandas_ta":
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    df = _sample_df()
    res = compute_indicators(df, params={}, engine="pandas_ta")
    res2 = compute_indicators(df, params={}, engine="builtin")
    pd.testing.assert_series_equal(res["EMA_10"], res2["EMA_10"])
