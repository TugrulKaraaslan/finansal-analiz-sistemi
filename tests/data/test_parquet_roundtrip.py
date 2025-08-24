from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtest.cli import convert_to_parquet
from backtest.data.loader import load_prices


def test_parquet_roundtrip(tmp_path):
    df = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", periods=3),
            "Close": [1.0, 2.0, 3.0],
        }
    )
    excel_dir = tmp_path / "data"
    excel_dir.mkdir()
    df.to_excel(excel_dir / "AAA.xlsx", index=False)
    out_dir = tmp_path / "out"
    convert_to_parquet(str(excel_dir), str(out_dir))
    loaded = load_prices(["AAA"], backend="pandas", parquet_dir=out_dir)
    assert list(loaded.columns) == ["Date", "Close", "Symbol"]
    assert loaded["Close"].dtype == "float64"
    assert loaded["Date"].dtype == "datetime64[ns]"
