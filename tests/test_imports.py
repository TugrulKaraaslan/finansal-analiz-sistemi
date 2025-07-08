"""Unit tests for imports."""

import importlib


def test_pandas_ta_available():
    """The optional ``pandas_ta`` package should be importable."""
    assert importlib.util.find_spec("pandas_ta") is not None
