"""Unit tests for transpose."""

import pandas as pd
import pytest

from finansal_analiz_sistemi.utils.compat import transpose


def test_transpose_reverse_axes():
    """Transposing should swap axes when ``axis0`` and ``axis1`` differ."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = transpose(df, axis0=1, axis1=0)
    expected = df.transpose()
    assert result.equals(expected)


def test_transpose_invalid_axis():
    """Invalid axis values must raise ``ValueError``."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        transpose(df, axis0=0, axis1=2)


def test_transpose_same_axis_returns_copy():
    """Using identical axes should return a copy of the input frame."""
    df = pd.DataFrame({"a": [1, 2]})
    result = transpose(df, axis0=0, axis1=0)
    assert result.equals(df)
    assert result is not df
