import pandas as pd

from utils.compat import safe_concat, safe_to_excel


def test_safe_to_excel(tmp_path):
    """Test test_safe_to_excel."""
    df = pd.DataFrame({"a": [1]})
    file = tmp_path / "t.xlsx"
    with pd.ExcelWriter(file) as wr:
        safe_to_excel(df, wr, sheet_name="Test", index=False)
    assert file.exists()


def test_safe_concat_empty():
    """Test test_safe_concat_empty."""
    out = safe_concat([])
    assert out.empty and isinstance(out, pd.DataFrame)
