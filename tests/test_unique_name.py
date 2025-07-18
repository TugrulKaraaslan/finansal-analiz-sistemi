"""Unit tests for unique_name."""

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
