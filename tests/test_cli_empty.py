from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

import click
from backtest import cli


def _cfg():
    return SimpleNamespace(
        project=SimpleNamespace(
            out_dir="out",
            start_date=None,
            end_date=None,
            holding_period=1,
            transaction_cost=0.0,
            raise_on_error=False,
        ),
        data=SimpleNamespace(filters_csv="dummy.csv"),
        calendar=SimpleNamespace(
            tplus1_mode="price", holidays_source="none", holidays_csv_path=None
        ),
        indicators=SimpleNamespace(params={}, engine="pandas_ta"),
        benchmark=SimpleNamespace(xu100_source="none", xu100_csv_path=None),
        report=SimpleNamespace(
            daily_sheet_prefix="SCAN_",
            summary_sheet_name="SUMMARY",
            percent_format="0.00%",
        ),
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
    monkeypatch.setattr(cli, "compute_indicators", lambda df, params, engine=None: df)
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close>0"], "Group": ["G"]}
    )
    monkeypatch.setattr(cli, "load_filters_csv", lambda _: filters_df)

    def _run_screener(df, filters, d, strict=None, raise_on_error=None):
        assert raise_on_error is False
        assert strict is True
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])

    monkeypatch.setattr(cli, "run_screener", _run_screener)
    monkeypatch.setattr(
        cli,
        "run_1g_returns",
        lambda df, sigs, holding_period, transaction_cost, **kwargs: pd.DataFrame(
            columns=[
                "FilterCode",
                "Symbol",
                "Date",
                "EntryClose",
                "ExitClose",
                "Side",
                "ReturnPct",
                "Win",
                "Reason",
            ]
        ),
    )
    monkeypatch.setattr(cli, "write_reports", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())
    cli.scan_range.callback("cfg.yml", None, None, None, None)


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
    monkeypatch.setattr(cli, "compute_indicators", lambda df, params, engine=None: df)
    filters_df = pd.DataFrame(
        {"FilterCode": ["F1"], "PythonQuery": ["close>0"], "Group": ["G"]}
    )
    monkeypatch.setattr(cli, "load_filters_csv", lambda _: filters_df)

    def _run_screener(df, filters, d, strict=None, raise_on_error=None):
        assert raise_on_error is False
        assert strict is True
        return pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])

    monkeypatch.setattr(cli, "run_screener", _run_screener)
    monkeypatch.setattr(
        cli,
        "run_1g_returns",
        lambda df, sigs, holding_period, transaction_cost, **kwargs: pd.DataFrame(
            columns=[
                "FilterCode",
                "Symbol",
                "Date",
                "EntryClose",
                "ExitClose",
                "Side",
                "ReturnPct",
                "Win",
                "Reason",
            ]
        ),
    )
    monkeypatch.setattr(cli, "write_reports", lambda *args, **kwargs: {})
    monkeypatch.setattr(cli, "dataset_summary", lambda df: pd.DataFrame())
    monkeypatch.setattr(cli, "quality_warnings", lambda df: pd.DataFrame())
    cli.scan_day.callback("cfg.yml", "2024-01-02", None, None)


def test_scan_range_missing_excel(monkeypatch):
    cfg = _cfg()
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)

    def _raise(_):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(cli, "read_excels_long", _raise)
    with pytest.raises(click.ClickException) as exc:
        cli.scan_range.callback("cfg.yml", None, None, None, None)
    assert "missing" in str(exc.value)
