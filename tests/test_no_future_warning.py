import warnings

import pandas as pd

from utils.compat import safe_concat, safe_to_excel


def test_no_future_warning(tmp_path):
    """Test test_no_future_warning."""
    df = pd.DataFrame({"a": [1]})
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("error", FutureWarning)
        _ = safe_concat([df, pd.DataFrame()])
        out = tmp_path / "out.xlsx"
        with pd.ExcelWriter(out) as wr:
            safe_to_excel(df, wr, sheet_name="Test", index=False)
    assert not rec
    assert out.exists()
