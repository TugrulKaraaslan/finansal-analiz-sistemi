"""Unit tests for iso_date."""

from utils.date_utils import parse_date


def test_parse_date_formats():
    """Test test_parse_date_formats."""
    assert parse_date("07.03.2025").day == 7
    assert parse_date("2025-03-07").month == 3
