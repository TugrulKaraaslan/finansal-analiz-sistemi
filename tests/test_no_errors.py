"""Unit tests for no_errors."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.slow
def test_no_errors(tmp_path):
    """Test test_no_errors."""
    pkg_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests", "-k", "not test_no_errors"],
        capture_output=True,
        text=True,
        cwd=pkg_root,
    )
    assert "ERROR" not in result.stdout
