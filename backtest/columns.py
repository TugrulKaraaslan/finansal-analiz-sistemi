from __future__ import annotations

from typing import Dict, Iterable

from backtest.naming.aliases import normalize_token


def canonicalize(name: str) -> str:
    """Return canonical snake_case token for *name*."""
    return normalize_token(name)


def canonical_map(columns: Iterable[str]) -> Dict[str, str]:
    """Map ``{canonical: original}`` for an iterable of column names."""
    out: Dict[str, str] = {}
    for c in columns:
        can = canonicalize(c)
        out.setdefault(can, c)
    return out


__all__ = ["canonicalize", "canonical_map"]
