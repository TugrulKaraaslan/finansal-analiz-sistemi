import pandas as pd

from backtest.screener import run_screener


def test_run_screener_deduplicates():
    df_ind = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-02", "2024-01-02"]).normalize(),
            "open": [1.0, 1.0],
            "high": [1.0, 1.0],
            "low": [1.0, 1.0],
            "close": [1.0, 1.0],
            "volume": [100, 100],
        }
    )
    filters = pd.DataFrame(
        {
            "FilterCode": ["F1"],
            "PythonQuery": ["close > 0"],
        }
    )
    res = run_screener(df_ind, filters, pd.Timestamp("2024-01-02"))
    assert len(res) == 1
    assert res["Symbol"].tolist() == ["AAA"]
