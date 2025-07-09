"""Unit tests for no_pkg_conflict."""

import subprocess
import sys

import pytest


@pytest.mark.slow
def test_no_pkg_conflict():
    """Ensure package dependencies are consistent and tests still run."""
    pip_check = subprocess.run(
        [sys.executable, "-m", "pip", "check"], capture_output=True, text=True
    )
    assert "ERROR" not in pip_check.stdout

    pytest_run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_marker_slow.py"],
        capture_output=True,
        text=True,
    )
    assert "ERROR" not in pytest_run.stdout
