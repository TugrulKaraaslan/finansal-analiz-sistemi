"""Unit tests for unique_name."""

from utilities.naming import unique_name


def test_unique_name_helper():
    """``unique_name`` should append a counter when names clash."""
    seen = {"ema_10", "ema_10_1"}
    assert unique_name("ema_10", seen) == "ema_10_2"
    assert "ema_10_2" in seen
