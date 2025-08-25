import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "backtest.cli", "-h"],
        check=True,
        capture_output=True,
    )
    assert result.returncode == 0
