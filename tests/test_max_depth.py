"""Unit tests for max_depth."""

import pandas as pd
import pytest

import filter_engine as fe
import settings


def _nested(depth: int):
    """Return a nested filter expression ``depth`` levels deep."""
    expr = "x>0"
    for i in range(depth, 0, -1):
        expr = {"code": f"F{i}", "sub_expr": expr}
    return expr


def test_max_depth_guard(monkeypatch):
    """Evaluation should fail when filter nesting exceeds the limit."""
    df = pd.DataFrame({"x": [1]})
    monkeypatch.setattr(settings, "MAX_FILTER_DEPTH", 5)
    with pytest.raises(fe.QueryError):
        fe.safe_eval(_nested(6), df)
    monkeypatch.setattr(settings, "MAX_FILTER_DEPTH", 7)
    fe.safe_eval(_nested(6), df)
