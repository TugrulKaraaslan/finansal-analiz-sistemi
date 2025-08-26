from __future__ import annotations

import re
import warnings

import pandas as pd

from backtest.filters.normalize_expr import normalize_expr
from backtest.naming.aliases import normalize_token

ALLOW_FUNCS = {"cross_up", "cross_down"}
ALLOWED_PATTERNS = [
    r"(?:ema|sma|wma|hma|vwma|dema|tema)_\d+",
    r"rsi_\d+",
    r"stoch[dk]_\d+_\d+_\d+",
    r"stochrsi_[kd]_\d+_\d+_\d+_\d+",
    r"bb[uml]_\d+_\d+",
    r"atr_\d+",
    r"macd_line",
    r"macd_signal",
    r"change_\d+[dwm]_percent",
    r"relative_volume",
    r"psar.*",
]


def _tokens(expr: str) -> list[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or "")


def validate_filters(
    filters_df: pd.DataFrame,
    dataset_df: pd.DataFrame,
    alias_mode: str = "allow",  # 'allow'|'warn'|'forbid'
    allow_unknown: bool = False,
) -> None:
    cols = {normalize_token(c) for c in dataset_df.columns}
    alias_used: dict[str, set[str]] = {}
    unknown: dict[str, set[str]] = {}

    for _, row in filters_df.iterrows():
        code = (row.get("FilterCode") or "").strip() or "<NO_CODE>"
        expr_raw = (row.get("PythonQuery") or "").strip()
        expr = normalize_expr(expr_raw)[0]
        for t in _tokens(expr):
            canon = normalize_token(t)
            if canon != t:
                alias_used.setdefault(code, set()).add(f"{t}->{canon}")
            if (
                canon in ALLOW_FUNCS
                or canon in cols
                or any(re.fullmatch(p, canon) for p in ALLOWED_PATTERNS)
            ):
                continue
            unknown.setdefault(code, set()).add(canon)

    if alias_used:
        lines = [f"{k}: {sorted(vs)}" for k, vs in alias_used.items()]
        if alias_mode == "forbid":
            msg = "Preflight failed. Legacy aliases detected:\n  "
            msg += "\n  ".join(lines)
            raise SystemExit(msg)
        elif alias_mode == "warn":
            for k, vs in alias_used.items():
                warnings.warn(f"Preflight: legacy alias in {k}: {sorted(vs)}")

    if unknown:
        lines = [f"{k}: {sorted(v)}" for k, v in unknown.items()]
        msg = "Preflight unknown tokens:\n  " + "\n  ".join(lines)
        if allow_unknown:
            warnings.warn(msg)
        else:
            raise SystemExit("Preflight failed. " + msg)
