from __future__ import annotations

import difflib
from typing import Iterable

import pandas as pd

from backtest.filters.deps import collect_series


class UnknownSeriesError(SystemExit):
    pass


def check_unknown_series(df: pd.DataFrame, exprs: Iterable[str]) -> None:
    """Fail with FR001 if an expression references unknown series names."""

    needed = collect_series(exprs)
    missing = sorted(name for name in needed if name not in df.columns)
    if not missing:
        return

    suggestions = {}
    universe = list(df.columns)
    for name in missing:
        suggestions[name] = difflib.get_close_matches(name, universe, n=3)

    lines = ["FR001: unknown series -> " + ", ".join(missing)]
    for name, sugg in suggestions.items():
        if sugg:
            lines.append(f"  {name}: did you mean {', '.join(sugg)}?")
    raise UnknownSeriesError("\n".join(lines))


__all__ = ["check_unknown_series", "UnknownSeriesError"]
