"""Safe evaluation for DataFrame queries."""
from __future__ import annotations

import ast
import string
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
    }

    def __init__(self, expr: str):
        self.expr = expr
        ok, names, err = self._validate(expr)
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

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows from *df* matching the query expression.

        Raises
        ------
        ValueError
            If the stored expression is unsafe.
        """
        if not self.is_safe:
            raise ValueError(f"Unsafe query expression: {self.error}")
        return df.query(self.expr)
