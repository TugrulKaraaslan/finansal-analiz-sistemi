"""Safe evaluation for DataFrame queries."""

from __future__ import annotations

import ast
import re
import string
from typing import Set, Tuple

import numpy as np
import pandas as pd

from backtest.naming import normalize_name
from .cross import cross_up, cross_down, cross_over, cross_under


class SafeQuery:
    """Validate and run pandas ``DataFrame.query`` expressions.

    Parameters
    ----------
    expr:
        The query expression to validate. Validation checks for
        disallowed characters and AST nodes that may lead to unsafe
        execution. The expression is considered safe if it only contains
        allowed characters and does not include unapproved function
        calls or attribute access.
    """

    # characters permitted inside a query expression
    _ALLOWED_CHARS: Set[str] = set("()&|><=+-/*.%[], '~") | set(
        string.ascii_letters + string.digits + '_"'
    )
    _ALLOWED_FUNCS: Set[str] = {
        "isin",
        "notna",
        "str",
        "contains",
        "abs",
        "rolling",
        "shift",
        "mean",
        "max",
        "min",
        "std",
        "median",
        "log",
        "exp",
        "floor",
        "ceil",
        "CROSSUP",
        "crossup",
        "CROSSDOWN",
        "crossdown",
        "CROSSOVER",
        "crossover",
        "CROSSUNDER",
        "crossunder",
        "CROSS_UP",
        "cross_up",
        "CROSS_DOWN",
        "cross_down",
    }

    def __init__(self, expr: str):
        expr_tr = re.sub(r"\band\b", "&", expr, flags=re.I)
        expr_tr = re.sub(r"\bor\b", "|", expr_tr, flags=re.I)
        expr_tr = re.sub(r"\bnot\b", "~", expr_tr, flags=re.I)

        class _Canon(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id in SafeQuery._ALLOWED_FUNCS:
                    return node
                node.id = normalize_name(node.id)
                return node

        tree = ast.parse(expr_tr, mode="eval")
        tree = _Canon().visit(tree)
        ast.fix_missing_locations(tree)
        expr_tr = ast.unparse(tree)

        self.expr = expr_tr
        ok, names, err = self._validate(expr_tr)
        self.is_safe = ok
        self.names = {normalize_name(n) for n in names}
        self.error = err

    @classmethod
    def _validate(cls, expr: str) -> Tuple[bool, Set[str], str | None]:
        """Return (is_safe, names, error_message) for *expr*."""
        names: Set[str] = set()
        # quick character check
        invalid = next(
            (ch for ch in expr if ch not in cls._ALLOWED_CHARS), None)
        if invalid is not None:
            return False, names, f"invalid character {invalid!r}"
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            return False, names, "syntax error"
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id not in cls._ALLOWED_FUNCS:
                    names.add(node.id)
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr not in cls._ALLOWED_FUNCS:
                        return (
                            False,
                            names,
                            f"function '{func.attr}' not allowed",
                        )
                elif isinstance(func, ast.Name):
                    if func.id not in cls._ALLOWED_FUNCS:
                        return (
                            False,
                            names,
                            f"function '{func.id}' not allowed",
                        )
                else:
                    return False, names, "invalid function call"
            elif isinstance(node, ast.Attribute):
                if node.attr not in cls._ALLOWED_FUNCS:
                    return False, names, f"attribute '{node.attr}' not allowed"
        return True, names, None

    def get_mask(self, df: pd.DataFrame) -> pd.Series:
        if not self.is_safe:
            raise ValueError(f"Unsafe query expression: {self.error}")
        env = {name: df[name] for name in df.columns}
        env.update(
            {
                "abs": abs,
                "max": max,
                "min": min,
                "log": np.log,
                "exp": np.exp,
                "floor": np.floor,
                "ceil": np.ceil,
                "CROSSUP": lambda a, b: cross_up(a, b),
                "crossup": lambda a, b: cross_up(a, b),
                "CROSSDOWN": lambda a, b: cross_down(a, b),
                "crossdown": lambda a, b: cross_down(a, b),
                "CROSSOVER": lambda a, level: cross_over(a, level),
                "crossover": lambda a, level: cross_over(a, level),
                "CROSSUNDER": lambda a, level: cross_under(a, level),
                "crossunder": lambda a, level: cross_under(a, level),
                "CROSS_UP": lambda a, b: cross_up(a, b),
                "cross_up": lambda a, b: cross_up(a, b),
                "CROSS_DOWN": lambda a, b: cross_down(a, b),
                "cross_down": lambda a, b: cross_down(a, b),
            }
        )
        mask = pd.eval(self.expr, engine="python",
                       parser="pandas", local_dict=env)
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError(
                "Query expression must evaluate to a boolean mask")
        return mask

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows from *df* matching the query expression."""
        mask = self.get_mask(df)
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError(
                "Query expression must evaluate to a boolean mask")
        return df[mask]
