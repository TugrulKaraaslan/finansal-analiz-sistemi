"""Unit tests for swapaxes."""

import pandas as pd
import pytest

from finansal_analiz_sistemi.utils import swapaxes


def test_swapaxes_basic():
    """Swapaxes wrapper should behave like ``DataFrame.T`` by default."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = swapaxes(df)
    expected = df.T
    pd.testing.assert_frame_equal(out, expected)


def test_swapaxes_axis_args():
    """Swapaxes accepts axis parameters identical to ``DataFrame.swapaxes``."""
    df = pd.DataFrame({"x": [5, 6]})
    out = swapaxes(df, 0, 1)
    expected = df.T
    pd.testing.assert_frame_equal(out, expected)


def test_swapaxes_invalid_axis():
    """Invalid axis values raise ``ValueError``."""
    df = pd.DataFrame({"x": [5, 6]})
    with pytest.raises(ValueError):
        swapaxes(df, 2, 0)
