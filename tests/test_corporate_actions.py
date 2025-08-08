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


def _apply_loop(df, adj):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    adj = adj.copy()
    adj["date"] = pd.to_datetime(adj["date"]).dt.normalize()
    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    for sym, grp in adj.groupby("symbol"):
        for _, row in grp.sort_values("date").iterrows():
            mask = (df["symbol"] == sym) & (df["date"] < row["date"])
            df.loc[mask, price_cols] = df.loc[mask, price_cols] * float(row["factor"])
    return df


def test_apply_corporate_actions_equivalence(tmp_path):
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 3,
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "open": [10.0, 20.0, 30.0],
            "high": [10.0, 20.0, 30.0],
            "low": [10.0, 20.0, 30.0],
            "close": [10.0, 20.0, 30.0],
            "volume": [100, 200, 300],
        }
    )
    adj = pd.DataFrame(
        {
            "symbol": ["AAA", "AAA"],
            "date": ["2024-01-02", "2024-01-03"],
            "factor": [0.5, 0.5],
        }
    )
    csv = tmp_path / "actions.csv"
    adj.to_csv(csv, index=False)
    vec = apply_corporate_actions(df, csv)
    manual = _apply_loop(df, adj)
    pd.testing.assert_frame_equal(vec, manual)
