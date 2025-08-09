"""Safe evaluation for DataFrame queries."""
from __future__ import annotations

import ast
import string
import re
from typing import Set, Tuple

import pandas as pd


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
    _ALLOWED_CHARS: Set[str] = set("()&|><=+-/*.%[], '") | set(
        string.ascii_letters + string.digits + "_\""
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
    }

    def __init__(self, expr: str):
        expr_tr = re.sub(r"\band\b", "&", expr, flags=re.I)
        expr_tr = re.sub(r"\bor\b", "|", expr_tr, flags=re.I)
        expr_tr = re.sub(r"\bnot\b", "~", expr_tr, flags=re.I)
        self.expr = expr_tr
        ok, names, err = self._validate(expr_tr)
        self.is_safe = ok
        self.names = names
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
                names.add(node.id)
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    if func.attr not in cls._ALLOWED_FUNCS:
                        return False, names, f"function '{func.attr}' not allowed"
                elif isinstance(func, ast.Name):
                    if func.id not in cls._ALLOWED_FUNCS:
                        return False, names, f"function '{func.id}' not allowed"
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
        env.update({"abs": abs, "max": max, "min": min})
        mask = pd.eval(
            self.expr, engine="python", parser="pandas", local_dict=env
        )
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError("Query expression must evaluate to a boolean mask")
        return mask

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows from *df* matching the query expression."""
        mask = self.get_mask(df)
        if not pd.api.types.is_bool_dtype(mask):
            raise ValueError("Query expression must evaluate to a boolean mask")
        return df[mask]
