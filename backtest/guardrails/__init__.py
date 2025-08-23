"""Guardrail utilities for preventing look-ahead bias."""

from .no_lookahead import (
    assert_monotonic_index,
    enforce_t_plus_one,
    check_warmup,
    detect_future_refs,
    verify_alignment,
)

__all__ = [
    "assert_monotonic_index",
    "enforce_t_plus_one",
    "check_warmup",
    "detect_future_refs",
    "verify_alignment",
]
