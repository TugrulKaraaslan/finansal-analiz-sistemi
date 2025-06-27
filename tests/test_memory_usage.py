import subprocess
from pathlib import Path

import pandas as pd
import psutil


def test_memory_usage(tmp_path: Path):
    csv = tmp_path / "mini.csv"
    pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=100),
            "ticker": "AAA",
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 100,
        }
    ).to_csv(csv, index=False)

    cmd = [
        "python",
        "-m",
        "finansal.cli",
        "--csv",
        str(csv),
        "--ind-set",
        "core",
        "--refresh-cache",
    ]
    proc = subprocess.Popen(cmd)
    proc.wait(timeout=60)
    if psutil.pid_exists(proc.pid):
        mem = psutil.Process(proc.pid).memory_info().rss / (1024**2)
    else:
        mem = 0
    assert mem < 200, f"RSS {mem:.1f} MB > 200 MB"
