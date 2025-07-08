"""Unit tests for passive_filter."""

import pandas as pd

from filter_engine import run_filter


def test_passive_filter_skipped(monkeypatch):
    """Passive filters should return an empty DataFrame."""
    df = pd.DataFrame({"x": [1, 2, 3]})
    res = run_filter(code="T31", df=df, expr={"sub_expr": "x>0"})
    assert res.empty
