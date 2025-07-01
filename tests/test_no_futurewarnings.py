import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.slow
def test_no_futurewarnings(tmp_path):
    pkg_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests",
            "-k",
            "not test_no_futurewarnings",
            "-W",
            "ignore::ResourceWarning",
        ],
        capture_output=True,
        text=True,
        cwd=pkg_root,
        env={**os.environ, "PYTHONWARNINGS": "ignore::ResourceWarning"},
    )
    assert "WARNING" not in result.stdout
