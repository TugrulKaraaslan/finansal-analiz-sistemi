"""Unit tests for filter_depth."""

import pandas as pd

from filter_engine import FAILED_FILTERS, safe_eval
from utils.failure_tracker import failures


def test_filter_depth_ok():
    """Test test_filter_depth_ok."""
    df = pd.DataFrame({"x": [1]})
    expr = {
        "code": "A",
        "sub_expr": {
            "code": "B",
            "sub_expr": {
                "code": "C",
                "sub_expr": {
                    "code": "D",
                    "sub_expr": {
                        "code": "E",
                        "sub_expr": {"code": "F", "sub_expr": "x>0"},
                    },
                },
            },
        },
    }
    failures.clear()
    FAILED_FILTERS.clear()
    result = safe_eval(expr, df)
    assert len(result) == 1
    assert len(failures["filters"]) == 0
