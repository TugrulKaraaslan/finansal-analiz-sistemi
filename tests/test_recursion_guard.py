"""Unit tests for recursion_guard."""

import pandas as pd
import pytest

from filter_engine import QueryError, safe_eval


def test_safe_eval_recursion_guard():
    """Test test_safe_eval_recursion_guard."""
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
                        "sub_expr": {
                            "code": "F",
                            "sub_expr": {
                                "code": "G",
                                "sub_expr": {"code": "H", "sub_expr": "x>0"},
                            },
                        },
                    },
                },
            },
        },
    }
    with pytest.raises(QueryError):
        safe_eval(expr, df)
