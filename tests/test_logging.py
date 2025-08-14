import json
import logging
import os
import time
from pathlib import Path

import pytest

from backtest.logging_utils import Timer, purge_old_logs, setup_logger


def _run_dir_from_logfile(logfile: str) -> Path:
    return Path(logfile).parent


def test_logs_dir_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logfile = setup_logger(run_id="t1")
    run_dir = _run_dir_from_logfile(logfile)
    assert run_dir.parent.name == "loglar"
    assert run_dir.name.startswith("run_")
    assert Path(logfile).exists()


def test_timer_records_stage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logfile = setup_logger(run_id="t2")
    with Timer("load_data") as t:
        t.update(rows=1, cols=2)
    run_dir = _run_dir_from_logfile(logfile)
    stage_file = run_dir / "stages.jsonl"
    assert stage_file.exists()
    data = json.loads(stage_file.read_text().splitlines()[0])
    assert data["stage"] == "load_data"
    assert data["rows"] == 1 and data["cols"] == 2


def test_error_logging(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logfile = setup_logger(run_id="t3")
    with pytest.raises(RuntimeError):
        with Timer("boom"):
            raise RuntimeError("boom")
    run_dir = _run_dir_from_logfile(logfile)
    err_file = run_dir / "boom.err"
    assert err_file.exists()
    stage_line = json.loads((run_dir / "stages.jsonl").read_text().splitlines()[0])
    assert stage_line["level"] == "ERROR"


def test_purge_old_logs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = Path("loglar")
    old_run = base / "run_old"
    new_run = base / "run_new"
    old_run.mkdir(parents=True)
    new_run.mkdir(parents=True)
    old_time = time.time() - 8 * 24 * 3600
    os.utime(old_run, (old_time, old_time))
    removed = purge_old_logs(days=7, log_dir=str(base))
    assert str(old_run) in removed
    assert not old_run.exists()
    assert new_run.exists()


def test_migration_warning(tmp_path, caplog, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("logs").mkdir()
    with caplog.at_level(logging.WARNING):
        setup_logger(run_id="t4")
    assert "legacy logs/ directory detected" in caplog.text
    assert Path("logs/migration.txt").exists()

