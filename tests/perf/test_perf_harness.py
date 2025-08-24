from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.perf_harness import main as perf_main


def test_perf_harness_creates_files(tmp_path, monkeypatch):
    outdir = tmp_path / "artifacts"
    monkeypatch.chdir(tmp_path)
    args = [
        "--scenario",
        "scan-day",
        "--backends",
        "pandas,polars",
        "--start",
        "2020-01-01",
        "--end",
        "2020-01-02",
        "--symbols",
        "AAA",
    ]
    # Create dummy data for loader
    data_dir = tmp_path / "data" / "parquet" / "symbol=AAA"
    data_dir.mkdir(parents=True)
    import pandas as pd

    pd.DataFrame({"Date": pd.date_range("2020-01-01", periods=2), "Close": [1.0, 2.0]}).to_parquet(
        data_dir / "AAA.parquet", index=False
    )
    monkeypatch.setattr(sys, "argv", ["perf_harness"] + args)
    perf_main()
    files = list((tmp_path / "artifacts/perf").glob("*.json"))
    assert files, "perf harness should write json files"
    for f in files:
        data = json.loads(f.read_text())
        assert "elapsed_sec" in data and "peak_kb" in data
