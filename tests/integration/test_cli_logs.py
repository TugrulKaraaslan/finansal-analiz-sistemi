import importlib
import logging
import os
from pathlib import Path

import pandas as pd
import pytest


def test_cli_emits_logs(tmp_path, monkeypatch):
    orig_cwd = os.getcwd()
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.chdir(tmp_path)

    for h in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(h)
    import backtest.logging_conf as logging_conf
    importlib.reload(logging_conf)
    import backtest.cli as cli
    importlib.reload(cli)

    df = pd.DataFrame({"close": [1.0]}, index=pd.to_datetime(["2025-03-07"]))
    monkeypatch.setattr(cli, "read_excels_long", lambda src: df)
    monkeypatch.setattr(cli, "run_scan_range", lambda *a, **k: None)
    monkeypatch.setattr(cli, "list_output_files", lambda *a, **k: [])
    monkeypatch.setattr(cli, "compile_filters", lambda *a, **k: None)
    filters_file = tmp_path / "f.csv"
    filters_file.write_text("FilterCode;PythonQuery\nF1;True\n", encoding="utf-8")
    monkeypatch.setattr(cli, "_resolve_filters_path", lambda _: filters_file)
    monkeypatch.setattr(cli, "load_filters_files", lambda paths: [{"FilterCode": "F1", "PythonQuery": "True"}])

    out_dir = tmp_path / "raporlar"
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        f"""
project:
  out_dir: "{out_dir.as_posix()}"
  start_date: "2025-03-07"
  end_date: "2025-03-07"
data:
  excel_dir: "{(tmp_path/'data').as_posix()}"
preflight: false
columns:
  column_date: "date"
  column_symbol: "symbol"
  column_close: "close"
filters:
  module: io_filters
""",
        encoding="utf-8",
    )

    args = [
        "scan-range",
        "--config",
        str(cfg_path),
        "--no-preflight",
        "--out",
        str(out_dir),
    ]
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    assert exc.value.code == 0

    log_dir = tmp_path / "loglar"
    jsonls = list(log_dir.glob("*.jsonl")) or list(tmp_path.rglob("*.jsonl"))
    assert jsonls, "no jsonl logs found under tmp_path"
    assert all(p.stat().st_size > 0 for p in jsonls), "empty jsonl log file(s) detected"

    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("LOG_FORMAT", raising=False)
    for h in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(h)
    os.chdir(orig_cwd)
    importlib.reload(logging_conf)
    importlib.reload(cli)
