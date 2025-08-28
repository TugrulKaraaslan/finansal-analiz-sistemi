from pathlib import Path

import numpy as np
import pandas as pd

from backtest.batch import run_scan_day, run_scan_range

# 5 iş günü, tek sembol için sentetik veri
idx = pd.date_range("2024-01-01", periods=5, freq="B")


def _df_single():
    np.random.seed(0)
    df = pd.DataFrame(
        {
            "open": [9, 10, 11, 10, 12],
            "high": [10, 11, 12, 11, 13],
            "low": [8, 9, 10, 9, 11],
            "close": [10, 10, 11, 10, 12],
            "volume": [100, 110, 120, 130, 140],
        },
        index=idx,
    )
    df.attrs["symbol"] = "SYM"
    return df


def _filters_df():
    return pd.DataFrame(
        {
            "FilterCode": ["F1", "F2"],
            "PythonQuery": [
                "CROSSUP(close, ema_20)",
                "close > 10 and volume > 100",
            ],
        }
    )


def test_run_scan_day_outputs_rows():
    df = _df_single()
    filters_df = _filters_df()
    rows = run_scan_day(df, str(idx[2].date()), filters_df)  # 3. gün
    # EMA20 NaN olabilir; ikinci kural çalışmalı
    assert ("SYM", "F2") in rows


def test_run_scan_range_writes_files(tmp_path: Path):
    df = _df_single()
    filters_df = _filters_df()
    out_dir = tmp_path / "gunluk"
    run_scan_range(
        df,
        str(idx[0].date()),
        str(idx[-1].date()),
        filters_df,
        out_dir=str(out_dir),
    )
    # 5 gün dosyası
    files = list(out_dir.glob("*.csv"))
    assert len(files) == 5
