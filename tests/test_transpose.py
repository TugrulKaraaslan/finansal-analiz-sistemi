"""Test module for test_transpose."""

import pandas as pd
import pytest

from finansal_analiz_sistemi.utils.compat import transpose


def test_transpose_reverse_axes():
    """Test test_transpose_reverse_axes."""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    result = transpose(df, axis0=1, axis1=0)
    expected = df.transpose()
    assert result.equals(expected)


def test_transpose_invalid_axis():
    """Test test_transpose_invalid_axis."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        transpose(df, axis0=0, axis1=2)


def test_transpose_same_axis_returns_copy():
    """Test test_transpose_same_axis_returns_copy."""
    df = pd.DataFrame({"a": [1, 2]})
    result = transpose(df, axis0=0, axis1=0)
    assert result.equals(df)
    assert result is not df
