import subprocess
import sys
from pathlib import Path


def test_no_pkg_conflict():
    pkg_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests",
            "-k",
            "not test_no_pkg_conflict",
        ],
        capture_output=True,
        text=True,
        cwd=pkg_root,
    )
    assert "ERROR" not in result.stdout
