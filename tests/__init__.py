"""Shared test utilities and global pytest configuration.

Fixtures defined here are imported across the test suite.
"""

import warnings

import pytest

# pytest sırasında açık dosya uyarısını bastır
warnings.filterwarnings(
    "ignore",
    message=r"Exception ignored in: <_io",
    category=pytest.PytestUnraisableExceptionWarning,
)
