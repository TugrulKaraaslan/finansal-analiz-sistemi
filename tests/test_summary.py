import pandas as pd
import numpy as np
from pathlib import Path
from backtest.summary import summarize_range

idx = pd.date_range("2024-01-01", periods=5, freq="B")


def _panel_multi():
    # 2 sembollü panel
    df = pd.DataFrame(index=idx)
    for sym, base in [("AAA", 10.0), ("BBB", 20.0)]:
        close = base + np.array([0, 1, 2, 1, 3], dtype=float)
        df[(sym, "close")] = close
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


def _signals_dir(tmp: Path):
    d = tmp / "gunluk"
    d.mkdir(parents=True, exist_ok=True)
    # 3 gün sinyal: 1. gün AAA, 2. gün AAA+BBB, 3. gün boş
    pd.DataFrame(
        {"date": [idx[0].date()], "symbol": ["AAA"], "filter_code": ["F1"]}
    ).to_csv(d / "2024-01-01.csv", index=False)
    pd.DataFrame(
        {
            "date": [idx[1].date(), idx[1].date()],
            "symbol": ["AAA", "BBB"],
            "filter_code": ["F1", "F2"],
        }
    ).to_csv(d / "2024-01-02.csv", index=False)
    pd.DataFrame(columns=["date", "symbol", "filter_code"]).to_csv(
        d / "2024-01-03.csv", index=False
    )
    return d


def _benchmark(tmp: Path):
    b = tmp / "bist.csv"
    pd.DataFrame(
        {"date": idx.date, "close": [100, 101, 102, 101, 103]}
    ).to_csv(  # noqa: E501
        b, index=False
    )
    return b


def test_summary_outputs(tmp_path: Path):
    panel = _panel_multi()
    out_dir = _signals_dir(tmp_path)
    bmk = _benchmark(tmp_path)
    res = summarize_range(
        panel, out_dir, str(bmk), horizon=1, write_dir=tmp_path / "ozet"
    )
    daily = pd.read_csv(
        res["daily_path"]
    )  # date,signals,filters,coverage,ew_ret,bist_ret,alpha
    assert len(daily) >= 2
    # 2024-01-01: AAA close 10→11 => 10%; BIST 100→101 => 1%; alpha ≈ 9%
    row1 = daily[daily["date"] == "2024-01-01"].iloc[0]
    assert abs(row1["ew_ret"] - 0.10) < 1e-6
    assert abs(row1["bist_ret"] - 0.01) < 1e-6
    assert abs(row1["alpha"] - 0.09) < 1e-6
