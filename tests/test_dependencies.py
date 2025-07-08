"""Unit tests for dependencies."""

import importlib.metadata
import importlib.util


def test_pandas_ta_openbb_installed():
    """Required ``pandas_ta`` plugin should be importable."""
    assert importlib.util.find_spec("pandas_ta") is not None
    assert importlib.metadata.version("pandas-ta-openbb")
