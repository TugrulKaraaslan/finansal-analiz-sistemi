from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from backtest import cli


def _cfg():
    return SimpleNamespace(
        project=SimpleNamespace(out_dir="out", start_date=None, end_date=None),
        data=SimpleNamespace(filters_csv="dummy.csv"),
        calendar=SimpleNamespace(tplus1_mode="price", holidays_source="none", holidays_csv_path=None),
        indicators=SimpleNamespace(params={}),
        benchmark=SimpleNamespace(xu100_source="none", xu100_csv_path=None),
        report=SimpleNamespace(daily_sheet_prefix="SCAN_", summary_sheet_name="SUMMARY", percent_format="0.00%"),
    )


def test_scan_range_empty(monkeypatch):
    cfg = _cfg()
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    dummy_df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).date,
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [1],
            "next_close": [1],
            "next_date": pd.to_datetime(["2024-01-03"]).date,
        }
    )
    monkeypatch.setattr(cli, "read_excels_long", lambda _: dummy_df)
    monkeypatch.setattr(cli, "normalize", lambda df: df)
    monkeypatch.setattr(cli, "add_next_close", lambda df: df)
    monkeypatch.setattr(cli, "compute_indicators", lambda df, params: df)
    monkeypatch.setattr(pd, "read_csv", lambda path: pd.DataFrame({"FilterCode": [], "PythonQuery": []}))
    monkeypatch.setattr(cli, "run_screener", lambda df, filters, d: pd.DataFrame(columns=["FilterCode", "Symbol", "Date", "mask"]))
    monkeypatch.setattr(cli, "run_1g_returns", lambda df, sigs: pd.DataFrame(columns=["FilterCode", "Symbol", "Date", "EntryClose", "ExitClose", "ReturnPct", "Win"]))
    monkeypatch.setattr(cli, "write_reports", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "info", lambda msg: None)
    monkeypatch.setattr(cli.os, "makedirs", lambda *args, **kwargs: None)
    cli.scan_range.callback("cfg.yml", None, None)


def test_scan_day_empty(monkeypatch):
    cfg = _cfg()
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    dummy_df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]).date,
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [1],
            "next_close": [1],
            "next_date": pd.to_datetime(["2024-01-03"]).date,
        }
    )
    monkeypatch.setattr(cli, "read_excels_long", lambda _: dummy_df)
    monkeypatch.setattr(cli, "normalize", lambda df: df)
    monkeypatch.setattr(cli, "add_next_close", lambda df: df)
    monkeypatch.setattr(cli, "compute_indicators", lambda df, params: df)
    monkeypatch.setattr(pd, "read_csv", lambda path: pd.DataFrame({"FilterCode": [], "PythonQuery": []}))
    monkeypatch.setattr(cli, "run_screener", lambda df, filters, d: pd.DataFrame(columns=["FilterCode", "Symbol", "Date", "mask"]))
    monkeypatch.setattr(cli, "run_1g_returns", lambda df, sigs: pd.DataFrame(columns=["FilterCode", "Symbol", "Date", "EntryClose", "ExitClose", "ReturnPct", "Win"]))
    monkeypatch.setattr(cli, "write_reports", lambda *args, **kwargs: None)
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "info", lambda msg: None)
    monkeypatch.setattr(cli.os, "makedirs", lambda *args, **kwargs: None)
    cli.scan_day.callback("cfg.yml", "2024-01-02")
