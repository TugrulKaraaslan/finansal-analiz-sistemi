import pandas as pd
import pytest
from filter_engine import safe_eval, QueryError


def test_safe_eval_recursion_guard():
    df = pd.DataFrame({"x": [1]})
    expr = {"sub_expr": {"sub_expr": {"sub_expr": {"sub_expr": {"sub_expr": {"clause": "x>0"}}}}}}
    with pytest.raises(QueryError):
        safe_eval(expr, df)
