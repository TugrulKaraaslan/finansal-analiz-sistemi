from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

import types, sys

fake_pa = types.ModuleType("pandera")
fake_pa.errors = types.SimpleNamespace(SchemaError=Exception)
fake_pa.DataFrameSchema = lambda *a, **k: None
fake_pa.Column = lambda *a, **k: None
sys.modules.setdefault("pandera", fake_pa)

from backtest.io.preflight import preflight
from backtest import cli


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
    real_dir = tmp_path / "veri"
    real_dir.mkdir()
    rep = preflight(tmp_path / "Veri", [date(2025, 3, 7)], "{date}.xlsx")
    assert rep.errors
    assert any("veri" in s.lower() for s in rep.suggestions)


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
  filters_csv: {}
""".format(tmp_path / "missing", tmp_path / "filters.csv"),
        encoding="utf-8",
    )
    (tmp_path / "filters.csv").write_text("FilterCode,PythonQuery\nF1,close > 0\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(cli.scan_day, ["--config", str(cfg_path), "--date", "2025-03-07"])
    assert result.exit_code != 0
    assert "Excel klasörü" in result.output
