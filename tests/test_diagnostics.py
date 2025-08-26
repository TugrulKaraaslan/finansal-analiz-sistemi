import json
import os
import logging
from pathlib import Path
from types import SimpleNamespace as NS

import pandas as pd
import pytest
from loguru import logger

from backtest import cli
from backtest.logging_utils import setup_logger
import backtest.data_loader as data_loader
import backtest.calendars as calendars
import backtest.indicators as indicators


def _setup_log(tmp_path):
    log_dir = tmp_path / "log"
    os.environ["LOG_DIR"] = str(log_dir)
    events_path = setup_logger(log_dir=str(log_dir))
    return Path(events_path)


def _assert_events(events_path: Path):
    lines = events_path.read_text().splitlines()
    assert lines
    first = json.loads(lines[0])
    assert {"stage", "metrics", "diag"}.issubset(first.keys())


def test_data_empty(tmp_path, caplog, monkeypatch):
    caplog.set_level("INFO")
    events_path = _setup_log(tmp_path)
    logger.add(caplog.handler, level="INFO")

    monkeypatch.setattr(cli, "read_excels_long", lambda cfg: pd.DataFrame())
    cfg = NS(project=NS(out_dir=str(tmp_path / "out")), data=NS(filters_csv=str(tmp_path / "f.csv")))
    cli._run_scan(cfg)

    assert "DATA_EMPTY" in caplog.text
    _assert_events(events_path)


def test_filters_empty(tmp_path, caplog, monkeypatch):
    caplog.set_level("INFO")
    events_path = _setup_log(tmp_path)
    logger.add(caplog.handler, level="INFO")

    dummy_df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [1],
        }
    )

    monkeypatch.setattr(cli, "read_excels_long", lambda cfg: dummy_df)
    monkeypatch.setattr(data_loader, "canonicalize_columns", lambda df: df)
    monkeypatch.setattr(calendars, "add_next_close_calendar", lambda df, t: df)
    monkeypatch.setattr(indicators, "compute_indicators", lambda df, params, engine=None: df)
    monkeypatch.setattr(cli, "load_filters_files", lambda paths: [])

    cfg = NS(
        project=NS(out_dir=str(tmp_path / "out")),
        data=NS(filters_csv=str(tmp_path / "filters.csv")),
        report=NS(daily_sheet_prefix="SCAN_", summary_sheet_name="SUMMARY", percent_format="0.00%"),
    )
    cli._run_scan(cfg)

    assert "FILTERS_EMPTY" in caplog.text
    _assert_events(events_path)


def test_no_match_day_zero_result(tmp_path, caplog, monkeypatch):
    caplog.set_level("INFO")
    events_path = _setup_log(tmp_path)
    logger.add(caplog.handler, level="INFO")

    dummy_df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [1],
        }
    )

    monkeypatch.setattr(cli, "read_excels_long", lambda cfg: dummy_df)
    monkeypatch.setattr(data_loader, "canonicalize_columns", lambda df: df)
    monkeypatch.setattr(calendars, "add_next_close_calendar", lambda df, t: df)
    monkeypatch.setattr(indicators, "compute_indicators", lambda df, params, engine=None: df)
    monkeypatch.setattr(cli, "load_filters_files", lambda paths: [{"FilterCode": "F1", "PythonQuery": "close>0"}])
    monkeypatch.setattr(
        cli,
        "run_screener",
        lambda df, filters, d, stop_on_filter_error, raise_on_error: pd.DataFrame(
            columns=["FilterCode", "Symbol", "Date"]
        ),
    )
    monkeypatch.setattr(
        cli,
        "run_1g_returns",
        lambda df, sigs, holding_period=1, transaction_cost=0.0, trading_days=None: pd.DataFrame(
            columns=[
                "FilterCode",
                "Symbol",
                "Date",
                "EntryClose",
                "ExitClose",
                "ReturnPct",
                "Win",
            ]
        ),
    )
    monkeypatch.setattr(cli, "write_reports", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())

    cfg = NS(
        project=NS(out_dir=str(tmp_path / "out")),
        data=NS(filters_csv=str(tmp_path / "filters.csv")),
        report=NS(daily_sheet_prefix="SCAN_", summary_sheet_name="SUMMARY", percent_format="0.00%"),
    )
    cli._run_scan(cfg)

    assert "NO_MATCH_DAY" in caplog.text
    assert "ZERO_RESULT_RANGE" in caplog.text
    _assert_events(events_path)


def test_positive_write_logs(tmp_path, caplog, monkeypatch):
    caplog.set_level("INFO")
    events_path = _setup_log(tmp_path)
    logger.add(caplog.handler, level="INFO")

    dummy_df = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-02"]),
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [1],
        }
    )

    monkeypatch.setattr(cli, "read_excels_long", lambda cfg: dummy_df)
    monkeypatch.setattr(data_loader, "canonicalize_columns", lambda df: df)
    monkeypatch.setattr(calendars, "add_next_close_calendar", lambda df, t: df)
    monkeypatch.setattr(indicators, "compute_indicators", lambda df, params, engine=None: df)
    monkeypatch.setattr(cli, "load_filters_files", lambda paths: [{"FilterCode": "F1", "PythonQuery": "close>0"}])

    monkeypatch.setattr(
        cli,
        "run_screener",
        lambda df, filters, d, stop_on_filter_error, raise_on_error: pd.DataFrame(
            {"FilterCode": ["F1"], "Symbol": ["AAA"], "Date": [pd.Timestamp(d)]}
        ),
    )
    monkeypatch.setattr(
        cli,
        "run_1g_returns",
        lambda df, sigs, holding_period=1, transaction_cost=0.0, trading_days=None: pd.DataFrame(
            {
                "FilterCode": ["F1"],
                "Symbol": ["AAA"],
                "Date": pd.to_datetime(["2024-01-02"]),
                "EntryClose": [1.0],
                "ExitClose": [1.1],
                "ReturnPct": [0.1],
                "Win": [True],
            }
        ),
    )
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())

    def fake_write_reports(trades_all, *, dates, out_xlsx=None, out_csv_dir=None, **kwargs):
        log = logging.getLogger("summary_bist")
        for d in dates:
            day_str = str(pd.to_datetime(d).date())
            rows = len(trades_all[trades_all["Date"] == pd.to_datetime(d)])
            log.info(
                "WRITE_DAY day=%s rows_written=%d xlsx_path=%s csv_path=%s",
                day_str,
                rows,
                out_xlsx,
                out_csv_dir,
            )
        log.info("WRITE_RANGE rows_total=%d out_dir=%s", len(trades_all), out_xlsx)
        return {}

    monkeypatch.setattr(cli, "write_reports", fake_write_reports)

    cfg = NS(
        project=NS(out_dir=str(tmp_path / "out")),
        data=NS(filters_csv=str(tmp_path / "filters.csv")),
        report=NS(daily_sheet_prefix="SCAN_", summary_sheet_name="SUMMARY", percent_format="0.00%"),
    )
    cli._run_scan(cfg)

    text = caplog.text
    assert ("WRITE_DAY" in text and "rows_written=1" in text) or (
        "WRITE_RANGE" in text and "rows_total=1" in text
    )
    _assert_events(events_path)
