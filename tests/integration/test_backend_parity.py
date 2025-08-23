from __future__ import annotations

import pandas as pd

from backtest.data.loader import load_prices


def test_backend_parity(tmp_path):
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-01", periods=5),
        "Close": range(5),
    })
    out_dir = tmp_path / "data"
    sym_dir = out_dir / "symbol=AAA"
    sym_dir.mkdir(parents=True)
    df.to_parquet(sym_dir / "AAA.parquet", index=False)
    pandas_df = load_prices(["AAA"], start="2020-01-02", end="2020-01-04", cols=["Date", "Close"], backend="pandas", parquet_dir=out_dir)
    polars_df = load_prices(["AAA"], start="2020-01-02", end="2020-01-04", cols=["Date", "Close"], backend="polars", parquet_dir=out_dir)
    pd.testing.assert_frame_equal(pandas_df, polars_df)
