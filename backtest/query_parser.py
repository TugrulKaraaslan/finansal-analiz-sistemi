"""Safe evaluation for DataFrame queries."""
from __future__ import annotations

import ast
import string
from typing import Set

import pandas as pd


class SafeQuery:
    """Validate and run pandas ``DataFrame.query`` expressions.

    Parameters
    ----------
    expr:
        The query expression to validate. Validation checks for
        disallowed characters and AST nodes that may lead to unsafe
        execution. The expression is considered safe if it only contains
        allowed characters and does not include :class:`ast.Call` or
        :class:`ast.Attribute` nodes.
    """

    # characters permitted inside a query expression
    _ALLOWED_CHARS: Set[str] = set("()&|><=+-/*.% ") | set(
        string.ascii_letters + string.digits + "_"
    )

    def __init__(self, expr: str):
        self.expr = expr
        self.is_safe = self._validate(expr)

    @classmethod
    def _validate(cls, expr: str) -> bool:
        """Return ``True`` if *expr* is safe to evaluate."""
        # quick character check
        if any(ch not in cls._ALLOWED_CHARS for ch in expr):
            return False
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            return False
        # disallow function calls and attribute access
        for node in ast.walk(tree):
            if isinstance(node, (ast.Call, ast.Attribute)):
                return False
        return True

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return rows from *df* matching the query expression.

        Raises
        ------
        ValueError
            If the stored expression is unsafe.
        """
        if not self.is_safe:
            raise ValueError("Unsafe query expression")
        return df.query(self.expr)
