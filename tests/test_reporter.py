from __future__ import annotations

import pathlib

import pandas as pd

from backtest.reporter import _ensure_dir, write_reports


def test_ensure_dir_handles_simple_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _ensure_dir("report.xlsx")  # should not raise
    assert pathlib.Path("report.xlsx").parent.exists()


def test_write_reports_returns_paths(tmp_path):
    trades = pd.DataFrame(
        {
            "FilterCode": ["f1"],
            "Symbol": ["SYM"],
            "Date": [pd.Timestamp("2024-01-01")],
            "EntryClose": [10.0],
            "ExitClose": [11.0],
            "ReturnPct": [10.0],
            "Win": [True],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    winrate = (
        trades.groupby(["FilterCode", "Date"])["Win"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    out_xlsx = tmp_path / "out.xlsx"
    out_csv_dir = tmp_path / "csv"
    outputs = write_reports(
        trades,
        [pd.Timestamp("2024-01-01")],
        summary,
        out_xlsx=out_xlsx,
        out_csv_dir=out_csv_dir,
        summary_winrate=winrate,
    )
    assert outputs["excel"] == out_xlsx.resolve()
    assert out_xlsx.exists()
    csv_names = {p.name for p in outputs.get("csv", [])}
    assert {"daily_trades.csv", "summary.csv", "summary_winrate.csv"}.issubset(csv_names)
    for p in outputs.get("csv", []):
        assert p.exists()
