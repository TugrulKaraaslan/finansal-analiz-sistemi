from __future__ import annotations
from pathlib import Path
import re
import warnings
import pandas as pd
from io_filters import read_filters_csv

ALIAS = {
    "its_9": "ichimoku_conversionline",
    "iks_26": "ichimoku_baseline",
    "macd_12_26_9": "macd_line",
    "macds_12_26_9": "macd_signal",
    "bbm_20 2": "bbm_20_2",
    "bbu_20 2": "bbu_20_2",
    "bbl_20 2": "bbl_20_2",
}
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


def _dataset_columns(excel_dir: Path) -> set[str]:
    xls = sorted([p for p in (excel_dir).rglob("*.xlsx")])
    assert xls, f"Preflight: Excel bulunamadı: {excel_dir}"
    df = pd.ExcelFile(xls[0]).parse(0, nrows=0)
    cols = set(map(str, df.columns))
    return cols | {c.lower() for c in cols}


def _tokens(expr: str) -> list[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or "")


def validate_filters(
    filters_csv: Path,
    excel_dir: Path,
    alias_mode: str = "allow",  # 'allow'|'warn'|'forbid'
    allow_unknown: bool = False,
) -> None:
    cols = _dataset_columns(excel_dir)
    alias_used: dict[str, set[str]] = {}
    unknown: dict[str, set[str]] = {}

    df = read_filters_csv(filters_csv)
    for _, row in df.iterrows():
        code = (row.get("FilterCode") or "").strip() or "<NO_CODE>"
        expr = (row.get("PythonQuery") or "").strip()
        for t in _tokens(expr):
            if t in ALIAS:
                alias_used.setdefault(code, set()).add(f"{t}->{ALIAS[t]}")
                continue
            if (
                t in ALLOW_FUNCS
                or t in cols
                or any(re.fullmatch(p, t) for p in ALLOWED_PATTERNS)
            ):
                continue
            unknown.setdefault(code, set()).add(t)

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
