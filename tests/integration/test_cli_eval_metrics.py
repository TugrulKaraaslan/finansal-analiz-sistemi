import os
import subprocess
import sys


def test_cli_eval_metrics_smoke():
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest.cli",
            "eval-metrics",
            "--start",
            "2025-03-07",
            "--end",
            "2025-03-11",
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode in (0,)
