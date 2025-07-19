"""Unit tests for :mod:`utils.compat` wrappers."""

import pandas as pd

from utils.compat import safe_concat, safe_to_excel


def test_safe_to_excel(tmp_path):
    """Ensure :func:`safe_to_excel` writes a file without errors."""
    df = pd.DataFrame({"a": [1]})
    file = tmp_path / "t.xlsx"
    with pd.ExcelWriter(file) as wr:
        safe_to_excel(df, wr, sheet_name="Test", index=False)
    assert file.exists()


def test_safe_concat_empty():
    """Ensure :func:`safe_concat` returns an empty DataFrame for empty input."""
    out = safe_concat([])
    assert out.empty and isinstance(out, pd.DataFrame)


def test_safe_concat_iterable():
    """safe_concat should accept any iterable of DataFrames."""
    frames = (pd.DataFrame({"a": [i]}) for i in range(3))
    result = safe_concat(frames, ignore_index=True)
    assert result.equals(pd.DataFrame({"a": [0, 1, 2]}))


def test_safe_concat_ignores_none():
    """None entries should be skipped during concatenation."""
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"a": [2]})
    result = safe_concat([df1, None, df2], ignore_index=True)
    assert result.equals(pd.DataFrame({"a": [1, 2]}))
