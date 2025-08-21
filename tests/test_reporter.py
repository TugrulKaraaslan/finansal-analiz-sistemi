from __future__ import annotations

import pathlib

import pandas as pd
import pytest

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
            "Side": ["long"],
            "ReturnPct": [10.0],
            "Win": [True],
            "Reason": [pd.NA],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Side", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    winrate = (
        trades.groupby(["FilterCode", "Side", "Date"])["Win"]
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
    assert {"daily_trades.csv", "summary.csv", "summary_winrate.csv"}.issubset(
        csv_names
    )
    for p in outputs.get("csv", []):
        assert p.exists()


def test_write_reports_preserves_excel_columns(tmp_path):
    trades = pd.DataFrame(
        {
            "FilterCode": ["f1"],
            "Symbol": ["SYM"],
            "Date": [pd.Timestamp("2024-01-01")],
            "EntryClose": [10.0],
            "ExitClose": [11.0],
            "Side": ["long"],
            "ReturnPct": [10.0],
            "Win": [True],
            "Reason": [pd.NA],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Side", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(
        trades,
        [pd.Timestamp("2024-01-01")],
        summary,
        out_xlsx=out_xlsx,
    )
    df = pd.read_excel(out_xlsx, sheet_name="SCAN_2024-01-01")
    assert list(df.columns) == list(trades.columns)


def test_write_reports_raises_on_excel_error(monkeypatch, tmp_path):
    trades = pd.DataFrame(
        {
            "FilterCode": ["f1"],
            "Symbol": ["SYM"],
            "Date": [pd.Timestamp("2024-01-01")],
            "EntryClose": [10.0],
            "ExitClose": [11.0],
            "Side": ["long"],
            "ReturnPct": [10.0],
            "Win": [True],
            "Reason": [pd.NA],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Side", "Date"])[
                       "ReturnPct"].mean().unstack()
    )

    def _bad_writer(*args, **kwargs):
        raise OSError("fail")

    monkeypatch.setattr(pd, "ExcelWriter", _bad_writer)
    with pytest.raises(RuntimeError):
        write_reports(
            trades,
            [pd.Timestamp("2024-01-01")],
            summary,
            out_xlsx=tmp_path / "out.xlsx",
        )


def test_write_reports_warns_if_file_missing(monkeypatch, tmp_path):
    trades = pd.DataFrame(
        {
            "FilterCode": ["f1"],
            "Symbol": ["SYM"],
            "Date": [pd.Timestamp("2024-01-01")],
            "EntryClose": [10.0],
            "ExitClose": [11.0],
            "Side": ["long"],
            "ReturnPct": [10.0],
            "Win": [True],
            "Reason": [pd.NA],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Side", "Date"])[
                       "ReturnPct"].mean().unstack()
    )
    out_xlsx = tmp_path / "out.xlsx"
    real_exists = pathlib.Path.exists

    def fake_exists(self):
        if self == out_xlsx.resolve():
            return False
        return real_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", fake_exists)
    with pytest.warns(UserWarning):
        write_reports(trades, [pd.Timestamp("2024-01-01")],
                      summary, out_xlsx=out_xlsx)


def test_write_reports_includes_trade_count(tmp_path):
    trades = pd.DataFrame(
        {
            "FilterCode": ["f1", "f1"],
            "Symbol": ["SYM1", "SYM2"],
            "Date": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-01")],
            "EntryClose": [10.0, 12.0],
            "ExitClose": [11.0, 13.0],
            "Side": ["long", "short"],
            "ReturnPct": [10.0, 8.333333333333332],
            "Win": [True, False],
            "Reason": [pd.NA, pd.NA],
        }
    )
    summary = (
        trades.groupby(["FilterCode", "Side", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    trade_counts = trades.groupby(["FilterCode", "Side"])["Symbol"].count()
    summary = summary.assign(TradeCount=trade_counts)
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(
        trades,
        [pd.Timestamp("2024-01-01")],
        summary,
        out_xlsx=out_xlsx,
    )
    df = pd.read_excel(out_xlsx, sheet_name="SUMMARY")
    assert "N_TRADES" in df.columns
    assert set(df["N_TRADES"]) == {1}
