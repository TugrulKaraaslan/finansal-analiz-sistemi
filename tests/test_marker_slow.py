"""Unit tests for marker_slow."""

import pytest


@pytest.mark.slow
def test_marker_slow():
    """Dummy slow test used to exercise pytest markers."""
    assert True
