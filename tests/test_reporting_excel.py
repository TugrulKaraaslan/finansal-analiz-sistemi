from pathlib import Path

import pandas as pd

from backtest.reporting import build_excel_report


def _make_inputs(tmp: Path):
    d = tmp / "ozet"
    d.mkdir(parents=True, exist_ok=True)
    daily = d / "daily_summary.csv"
    fcnt = d / "filter_counts.csv"
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "signals": [1, 2],
            "filters": [1, 2],
            "coverage": [1, 2],
            "ew_ret": [0.1, 0.0],
            "bist_ret": [0.01, 0.0],
            "alpha": [0.09, 0.0],
        }
    ).to_csv(daily, index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "filter_code": ["F1", "F2"],
            "count": [1, 2],
        }
    ).to_csv(fcnt, index=False)
    return daily, fcnt


def test_build_excel_report(tmp_path: Path):
    daily, fcnt = _make_inputs(tmp_path)
    out = tmp_path / "summary.xlsx"
    path = build_excel_report(daily, fcnt, out_xlsx=out)
    assert Path(path).exists()
