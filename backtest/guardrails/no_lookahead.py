"""Utilities to prevent look-ahead bias in backtests."""
from __future__ import annotations

from typing import Dict, Iterable
import ast
import pandas as pd

DENY_PATTERNS = ["shift(-", "lead(", "next_", "t+"]


def assert_monotonic_index(df: pd.DataFrame) -> None:
    idx = df.index
    if not idx.is_monotonic_increasing:
        raise AssertionError("index is not monotonic increasing")
    if idx.has_duplicates:
        raise AssertionError("index has duplicate entries")


def enforce_t_plus_one(exec_cfg: Dict | None = None) -> Dict:
    cfg = dict(exec_cfg or {})
    cfg["t_plus_one"] = True
    cfg["execution_price"] = cfg.get("execution_price", "open")
    cfg["delay"] = 1
    return cfg


def check_warmup(df: pd.DataFrame, min_bars: int) -> None:
    if min_bars <= 0:
        return
    if len(df) < min_bars:
        raise AssertionError("not enough data for warmup")
    head = df.iloc[:min_bars]
    if head.notna().any().any():
        raise AssertionError("warmup period contains signals")


def detect_future_refs(expr_or_ast, patterns: Iterable[str] | None = None) -> None:
    patterns = list(patterns or DENY_PATTERNS)
    if isinstance(expr_or_ast, ast.AST):
        text = ast.unparse(expr_or_ast)
    else:
        text = str(expr_or_ast)
    low = text.replace(" ", "").lower()
    for p in patterns:
        if p.lower().replace(" ", "") in low:
            raise AssertionError(f"future reference pattern detected: {p}")


def verify_alignment(dfs: Dict[str, pd.DataFrame]) -> None:
    items = list(dfs.items())
    if not items:
        return
    ref_name, ref_df = items[0]
    ref_index = ref_df.index
    for name, df in items[1:]:
        if len(df) != len(ref_df):
            raise AssertionError(f"length mismatch between {ref_name} and {name}")
        if not df.index.equals(ref_index):
            raise AssertionError(f"index mismatch between {ref_name} and {name}")
