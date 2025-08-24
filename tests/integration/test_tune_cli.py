import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_tune_cli(tmp_path):
    cfg = Path(__file__).resolve().parents[2] / "config/tune.yaml"
    cmd = [
        sys.executable,
        "-m",
        "backtest.cli",
        "tune-strategy",
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-20",
        "--space",
        str(cfg),
        "--search",
        "grid",
        "--max-iters",
        "5",
        "--seed",
        "42",
    ]
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[2])}
    subprocess.run(cmd, check=True, cwd=tmp_path, env=env)
    best = json.loads((tmp_path / "artifacts/tune/best_config.json").read_text())
    assert best == {"risk_per_trade_bps": 25, "atr_mult": 0}
    results = pd.read_csv(tmp_path / "artifacts/tune/cv_results.csv")
    assert "score" in results.columns
