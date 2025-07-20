"""Unit tests for unique_name."""

import pytest

from utilities.naming import unique_name


def test_unique_name_helper():
    """Ensure ``unique_name`` appends a counter when names clash."""
    seen = {"ema_10", "ema_10_1"}
    assert unique_name("ema_10", seen) == "ema_10_2"
    assert "ema_10_2" in seen


def test_unique_name_large_set():
    """Suffix should increment past the highest existing number."""
    seen = {"ema_10"} | {f"ema_10_{i}" for i in range(1, 11)}
    assert unique_name("ema_10", seen) == "ema_10_11"
    assert "ema_10_11" in seen


def test_unique_name_fills_gap():
    """Smallest unused suffix should be selected."""
    seen = {"ema_10", "ema_10_1", "ema_10_3"}
    assert unique_name("ema_10", seen) == "ema_10_2"
    assert "ema_10_2" in seen


def test_unique_name_trailing_underscore():
    """Trailing delimiter should not yield double underscores."""
    seen = {"foo_", "foo_1"}
    assert unique_name("foo_", seen) == "foo_2"
    assert "foo_2" in seen


def test_unique_name_multiple_trailing_delimiters():
    """Only one delimiter should be trimmed when ``base`` has repeats."""
    seen = {"bar__", "bar__1"}
    assert unique_name("bar__", seen) == "bar__2"
    assert "bar__2" in seen


def test_unique_name_empty_base_raises():
    """Empty ``base`` should trigger ``ValueError``."""
    with pytest.raises(ValueError):
        unique_name("", set())
