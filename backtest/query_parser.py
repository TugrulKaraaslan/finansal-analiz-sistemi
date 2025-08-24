"""Safe evaluation for DataFrame queries."""

from __future__ import annotations

import ast
import re
import string
from typing import Set, Tuple

import numpy as np
import pandas as pd

from backtest.naming import normalize_name
from .cross import cross_up as _cross_up, cross_down as _cross_down, cross_over


def _cross_up_env(a: pd.Series, b: pd.Series | float | int) -> pd.Series:
    if isinstance(b, pd.Series):
        out = _cross_up(a, b)
    else:
        out = cross_over(a, b)
    return out.fillna(False)


def _cross_down_env(a: pd.Series, b: pd.Series | float | int) -> pd.Series:
    if isinstance(b, pd.Series):
        if b.nunique() == 1:
            level = b.iloc[0]
            out = (a.shift(1) > level) & (a <= level)
        else:
            out = _cross_down(a, b)
    else:
        out = (a.shift(1) > b) & (a <= b)
    return out.fillna(False)


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
        "cross_up",
        "cross_down",
        "CROSSUP",
        "CROSSDOWN",
        "crossOver",
        "crossUnder",
        "cross_over",
        "cross_under",
        "keser_yukari",
        "keser_asagi",
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
        invalid = next((ch for ch in expr if ch not in cls._ALLOWED_CHARS), None)
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
                # canonical
                "cross_up": _cross_up_env,
                "cross_down": _cross_down_env,
                # aliases
                "CROSSUP": _cross_up_env,
                "CROSSDOWN": _cross_down_env,
                "crossOver": _cross_up_env,
                "crossUnder": _cross_down_env,
                "cross_over": _cross_up_env,
                "cross_under": _cross_down_env,
                "keser_yukari": _cross_up_env,
                "keser_asagi": _cross_down_env,
            }
        )
        mask = pd.eval(self.expr, engine="python", parser="pandas", local_dict=env)
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError("Query expression must evaluate to a boolean mask")
        return mask

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows from *df* matching the query expression."""
        mask = self.get_mask(df)
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError("Query expression must evaluate to a boolean mask")
        return df[mask]
