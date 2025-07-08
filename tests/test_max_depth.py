import pandas as pd
import pytest

import filter_engine as fe
import settings


def _nested(depth: int):
    """Test _nested."""
    expr = "x>0"
    for i in range(depth, 0, -1):
        expr = {"code": f"F{i}", "sub_expr": expr}
    return expr


def test_max_depth_guard(monkeypatch):
    """Test test_max_depth_guard."""
    df = pd.DataFrame({"x": [1]})
    monkeypatch.setattr(settings, "MAX_FILTER_DEPTH", 5)
    with pytest.raises(fe.QueryError):
        fe.safe_eval(_nested(6), df)
    monkeypatch.setattr(settings, "MAX_FILTER_DEPTH", 7)
    fe.safe_eval(_nested(6), df)
