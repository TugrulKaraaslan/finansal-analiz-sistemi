"""Unit tests for utils."""

import os
import sys

import numpy as np
import pandas as pd
import pytest

from utils import crosses_above, crosses_below

# Add the project root to ``sys.path`` for standalone execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_crosses_above_simple_numeric():
    """Detect when the first series crosses above the second."""
    s1 = pd.Series([1, 2, 3, 4])
    s2 = pd.Series([4, 3, 2, 1])
    result = crosses_above(s1, s2)
    expected = pd.Series([False, False, True, False])
    pd.testing.assert_series_equal(result, expected)


def test_crosses_below_simple_numeric():
    """Detect when the first series crosses below the second."""
    s1 = pd.Series([4, 3, 2, 1])
    s2 = pd.Series([1, 2, 3, 4])
    result = crosses_below(s1, s2)
    expected = pd.Series([False, False, True, False])
    pd.testing.assert_series_equal(result, expected)


def test_crosses_above_with_nan_returns_false():
    """NaN values should suppress cross-above signals."""
    s1 = pd.Series([1, 2, np.nan, 4])
    s2 = pd.Series([4, 3, 2, 1])
    result = crosses_above(s1, s2)
    expected = pd.Series([False, False, False, False])
    pd.testing.assert_series_equal(result, expected)


def test_crosses_below_with_nan_returns_false():
    """NaN values should suppress cross-below signals."""
    s1 = pd.Series([4, 3, np.nan, 1])
    s2 = pd.Series([1, 2, 3, 4])
    result = crosses_below(s1, s2)
    expected = pd.Series([False, False, False, False])
    pd.testing.assert_series_equal(result, expected)


@pytest.mark.parametrize("func", [crosses_above, crosses_below])
def test_cross_functions_equal_series_return_false(func):
    """Cross functions return all ``False`` when inputs are equal."""
    s = pd.Series([1, 1, 1, 1])
    result = func(s, s)
    expected = pd.Series([False, False, False, False], dtype=bool)
    pd.testing.assert_series_equal(result, expected)
    assert result.dtype == bool


def test_crosses_above_misaligned_index_length_matches_intersection():
    """Length matches index intersection for misaligned series (cross above)."""
    s1 = pd.Series([1, 2, 3, 4], index=[0, 1, 2, 3])
    s2 = pd.Series([4, 3, 2, 1], index=[2, 3, 4, 5])
    result = crosses_above(s1, s2)
    assert len(result) == len(s1.index.intersection(s2.index))


def test_crosses_below_misaligned_index_length_matches_intersection():
    """Length matches index intersection for misaligned series (cross below)."""
    s1 = pd.Series([4, 3, 2, 1], index=[0, 1, 2, 3])
    s2 = pd.Series([1, 2, 3, 4], index=[2, 3, 4, 5])
    result = crosses_below(s1, s2)
    assert len(result) == len(s1.index.intersection(s2.index))


@pytest.mark.parametrize("func", [crosses_above, crosses_below])
def test_cross_functions_with_none_returns_empty_false_series(func):
    """Passing ``None`` yields an empty ``False`` series."""
    s = pd.Series([1, 2, 3])
    result = func(None, s)
    expected = pd.Series(False, index=[])
    pd.testing.assert_series_equal(result, expected)


def test_cross_functions_all_nan_do_not_fail():
    """Cross functions handle all-NaN input without errors."""
    s_nan = pd.Series([np.nan, np.nan, np.nan])
    expected = pd.Series([False, False, False], index=s_nan.index, dtype=bool)
    result_above = crosses_above(s_nan, s_nan)
    result_below = crosses_below(s_nan, s_nan)
    pd.testing.assert_series_equal(result_above, expected)
    pd.testing.assert_series_equal(result_below, expected)
