"""Shared test utilities and global pytest configuration.

Fixtures defined here are imported across the test suite.
"""

import warnings

import pytest

# suppress open file warnings during pytest runs
warnings.filterwarnings(
    "ignore",
    message=r"Exception ignored in: <_io",
    category=pytest.PytestUnraisableExceptionWarning,
)
