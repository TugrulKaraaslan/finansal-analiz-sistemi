import subprocess
import sys
from pathlib import Path
import pandas as pd


def test_compare_cli(tmp_path):
    cfg = Path(__file__).resolve().parents[2] / "config/strategies.yaml"
    cmd = [
        sys.executable,
        "-m",
        "backtest.cli",
        "compare-strategies",
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-10",
        "--space",
        str(cfg),
    ]
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[2])}
    subprocess.run(cmd, check=True, cwd=tmp_path, env=env)
    out_csv = tmp_path / "artifacts/compare/results.csv"
    assert out_csv.exists()
    df = pd.read_csv(out_csv)
    expected_cols = {
        "id",
        "sharpe",
        "sortino",
        "cagr",
        "maxdd",
        "turnover",
        "hit_rate",
        "trades",
    }
    assert expected_cols.issubset(df.columns)

