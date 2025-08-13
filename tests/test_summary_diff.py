from __future__ import annotations

import pandas as pd

def test_summary_and_winrate():
    trades = pd.DataFrame(
        {
            "FilterCode": ["T1", "T1", "T1", "T2", "T2"],
            "Symbol": ["AAA", "BBB", "AAA", "AAA", "BBB"],
            "Date": pd.to_datetime(
                ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-02", "2024-01-03"]
            ).date,
            "ReturnPct": [1.0, -0.5, 2.0, 0.5, 0.0],
            "Win": [True, False, True, True, False],
        }
    )
    pivot = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    pivot["Ortalama"] = pivot.mean(axis=1)
    winrate = (
        trades.groupby(["FilterCode", "Date"])["Win"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    winrate["Ortalama"] = winrate.mean(axis=1)
    assert round(pivot.loc["T1"].mean(), 4) == round(pivot.loc["T1", "Ortalama"], 4)
    assert 0 <= winrate.min().min() <= 1 and 0 <= winrate.max().max() <= 1
