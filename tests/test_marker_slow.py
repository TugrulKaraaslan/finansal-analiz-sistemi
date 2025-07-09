"""Minimal test marked as slow for CI demonstrations."""

import pytest


@pytest.mark.slow
def test_marker_slow():
    """Dummy slow test used to exercise pytest markers."""
    assert True
