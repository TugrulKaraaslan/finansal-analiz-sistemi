"""Unit tests for safe_infer."""

import pandas as pd

from utils.compat import safe_infer_objects


def test_safe_infer_objects_copy_flag():
    """Verify ``safe_infer_objects`` handles the ``copy`` flag correctly."""
    df = pd.DataFrame({"a": [1]}, dtype=object)
    out = safe_infer_objects(df, copy=True)
    assert out is not df
    assert out["a"].dtype != object
    out2 = safe_infer_objects(df, copy=False)
    assert out2["a"].dtype != object
