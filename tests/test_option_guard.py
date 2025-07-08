"""Unit tests for option_guard."""

import pandas as pd

from utils.pandas_option_safe import ensure_option


def test_ensure_option_no_error():
    """ensure_option should not raise even if option is missing."""
    ensure_option("future.no_silent_downcasting", True)
    try:
        val = pd.get_option("future.no_silent_downcasting")
    except (AttributeError, KeyError, pd.errors.OptionError):
        return
    assert val is True
