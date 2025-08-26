from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))



def test_scan_range_help_shows_options() -> None:
    root = Path(__file__).resolve().parents[2]
    env = {**os.environ, "PYTHONPATH": str(root)}
    result = subprocess.run(
        [sys.executable, "-m", "backtest.cli", "scan-range", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert "--report-alias" in result.stdout
