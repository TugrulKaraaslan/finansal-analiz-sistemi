import pandas as pd

from backtest.data_loader import apply_corporate_actions


def test_apply_corporate_actions(tmp_path):
    df = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "open": [10.0, 20.0],
            "high": [10.0, 20.0],
            "low": [10.0, 20.0],
            "close": [10.0, 20.0],
            "volume": [100, 200],
        }
    )
    csv = tmp_path / "actions.csv"
    csv.write_text("symbol,date,factor\nAAA,2024-01-02,0.5\n", encoding="utf-8")
    adj = apply_corporate_actions(df, csv)
    first = adj.loc[adj["date"] == pd.Timestamp("2024-01-01"), "close"].iloc[0]
    second = adj.loc[adj["date"] == pd.Timestamp("2024-01-02"), "close"].iloc[0]
    assert first == 5.0
    assert second == 20.0
