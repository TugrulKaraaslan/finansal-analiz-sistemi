from __future__ import annotations

import sys
import types
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from click.testing import CliRunner

fake_pa = types.ModuleType("pandera")
fake_pa.errors = types.SimpleNamespace(SchemaError=Exception)
fake_pa.DataFrameSchema = lambda *a, **k: None
fake_pa.Column = lambda *a, **k: None
sys.modules.setdefault("pandera", fake_pa)

from backtest import cli  # noqa: E402
from backtest.io.preflight import preflight  # noqa: E402
from backtest.preflight import (  # noqa: E402
    UnknownSeriesError,
    check_unknown_series,
)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_preflight_all_found(tmp_path):
    dates = [date(2025, 3, 7), date(2025, 3, 10)]
    for d in dates:
        _touch(tmp_path / f"{d}.xlsx")
    rep = preflight(tmp_path, dates, "{date}.xlsx")
    assert not rep.errors
    assert not rep.missing_dates
    assert len(rep.found_files) == len(dates)


def test_preflight_missing_some(tmp_path):
    dates = [date(2025, 3, 7), date(2025, 3, 8)]
    _touch(tmp_path / "2025-03-07.xlsx")
    rep = preflight(tmp_path, dates, "{date}.xlsx")
    assert rep.missing_dates == [date(2025, 3, 8)]
    assert rep.warnings


def test_preflight_case_suggestion(tmp_path):
    real_dir = tmp_path / "data"
    real_dir.mkdir()
    rep = preflight(tmp_path / "Data", [date(2025, 3, 7)], "{date}.xlsx")
    assert rep.errors
    assert any("data" in s.lower() for s in rep.suggestions)


def test_preflight_filename_near_match(tmp_path):
    d = date(2025, 3, 7)
    _touch(tmp_path / "2025_03_07.xlsx")
    rep = preflight(tmp_path, [d], "{date}.xlsx")
    assert rep.missing_dates == [d]
    assert any("2025_03_07.xlsx" in s for s in rep.suggestions)


def test_preflight_fail_fast_on_errors(tmp_path):
    cfg_path = tmp_path / "cfg.yml"
    cfg_path.write_text(
        """
project:
  out_dir: out
  run_mode: single
  single_date: "2025-03-07"
  holding_period: 1
  transaction_cost: 0

data:
  excel_dir: {}  # missing
filters:
  module: io_filters
  include: ["*"]
""".format(
            tmp_path / "missing"
        ),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        cli.scan_day,
        ["--config", str(cfg_path), "--date", "2025-03-07"],
    )
    assert result.exit_code != 0
    assert "Excel klasörü" in result.output


def test_scan_day_no_preflight(monkeypatch):
    cfg = SimpleNamespace(
        project=SimpleNamespace(
            run_mode="single",
            single_date=None,
            holding_period=1,
            transaction_cost=0,
        ),
        data=SimpleNamespace(
            excel_dir=".",
            filename_pattern="{date}.xlsx",
            date_format="%Y-%m-%d",
            case_sensitive=True,
        ),
    )
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    called = False

    def _pf(*args, **kwargs):  # pragma: no cover - should not run
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "preflight", _pf)
    monkeypatch.setattr(cli, "_run_scan", lambda cfg: None)
    cli.scan_day.callback(
        "cfg.yml",
        "2025-03-07",
        None,
        None,
        no_preflight=True,
    )
    assert not called


def test_scan_day_case_insensitive(tmp_path, monkeypatch):
    cfg = SimpleNamespace(
        project=SimpleNamespace(
            run_mode="single",
            single_date=None,
            holding_period=1,
            transaction_cost=0,
        ),
        data=SimpleNamespace(
            excel_dir=tmp_path,
            filename_pattern="{date}.xlsx",
            date_format="%Y-%m-%d",
            case_sensitive=True,
        ),
    )
    _touch(tmp_path / "2025-03-07.XLSX")
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    monkeypatch.setattr(cli, "_run_scan", lambda cfg: None)
    runner = CliRunner()
    result = runner.invoke(
        cli.scan_day,
        ["--config", "cfg.yml", "--date", "2025-03-07", "--case-insensitive"],
    )
    assert result.exit_code == 0


def test_unknown_series_detection():
    df = pd.DataFrame({"close": [1, 2, 3]})
    exprs = ["stochrsik_14_14_3_3 > 0.8"]
    with pytest.raises(UnknownSeriesError) as exc:
        check_unknown_series(df, exprs)
    assert "FR001" in str(exc.value)
    assert "stochrsi_k_14_14_3_3" in str(exc.value)
