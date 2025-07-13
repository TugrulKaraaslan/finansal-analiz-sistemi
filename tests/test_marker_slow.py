"""Example test using the ``slow`` marker.

This file exists solely to illustrate how slow tests are handled in the
continuous integration workflow.
"""

import pytest


@pytest.mark.slow
def test_marker_slow():
    """Dummy slow test used to exercise pytest markers."""
    assert True
