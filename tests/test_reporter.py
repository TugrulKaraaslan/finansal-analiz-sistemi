from __future__ import annotations

import pathlib

from backtest.reporter import _ensure_dir


def test_ensure_dir_handles_simple_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _ensure_dir("report.xlsx")  # should not raise
    assert pathlib.Path("report.xlsx").parent.exists()
