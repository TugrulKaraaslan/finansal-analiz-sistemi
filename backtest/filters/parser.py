"""Thin wrapper around expression validation.

The real project contains a more sophisticated parser; for the tests in
this kata we only need to detect obvious future reference patterns.
"""
from __future__ import annotations

from backtest.guardrails.no_lookahead import detect_future_refs


def validate(expr: str) -> str:
    """Validate *expr* and return it.

    Raises :class:`AssertionError` if future data references are detected.
    """
    detect_future_refs(expr)
    return expr
