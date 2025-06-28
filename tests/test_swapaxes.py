import pandas as pd
import pytest

from finansal_analiz_sistemi.utils import swapaxes


def test_swapaxes_basic():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = swapaxes(df)
    expected = df.T
    pd.testing.assert_frame_equal(out, expected)


def test_swapaxes_axis_args():
    df = pd.DataFrame({"x": [5, 6]})
    out = swapaxes(df, 0, 1)
    expected = df.T
    pd.testing.assert_frame_equal(out, expected)


def test_swapaxes_invalid_axis():
    df = pd.DataFrame({"x": [5, 6]})
    with pytest.raises(ValueError):
        swapaxes(df, 2, 0)
