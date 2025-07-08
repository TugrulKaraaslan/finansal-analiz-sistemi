"""Test module for test_pandas_compat."""

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
