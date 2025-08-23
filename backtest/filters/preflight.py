from __future__ import annotations
from pathlib import Path
import csv
import re
import warnings
import pandas as pd

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
    r"macd_line", r"macd_signal",
    r"change_\d+[dwm]_percent",
    r"relative_volume",
    r"psar.*",
    r"sma\d*", r"ema\d*",
]


def _is_allowed_by_pattern(tok: str) -> bool:
    return any(re.fullmatch(p, tok) for p in ALLOWED_PATTERNS)


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
    fail_on_alias: bool = True,
    allow_unknown: bool = False,
) -> None:
    cols = _dataset_columns(excel_dir)
    bad: dict[str, set[str]] = {}
    alias_used: dict[str, set[str]] = {}

    with open(filters_csv, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            code = (row.get("FilterCode") or "").strip() or "<NO_CODE>"
            expr = (row.get("PythonQuery") or "").strip()
            for t in _tokens(expr):
                if t in ALIAS:
                    alias_used.setdefault(code, set()).add(f"{t}->{ALIAS[t]}")
                    continue
                if t in ALLOW_FUNCS or t in cols or _is_allowed_by_pattern(t):
                    continue
                bad.setdefault(code, set()).add(t)

    if alias_used:
        lines = [f"{k}: {sorted(vs)}" for k, vs in alias_used.items()]
        if fail_on_alias:
            raise SystemExit(
                "Preflight failed. Legacy aliases detected:\n  " + "\n  ".join(lines)
            )
        else:
            for k, vs in alias_used.items():
                warnings.warn(f"Preflight: legacy alias in {k}: {sorted(vs)}")

    if bad:
        lines = [f"{k}: {sorted(v)}" for k, v in bad.items()]
        msg = "Preflight unknown tokens:\n  " + "\n  ".join(lines)
        if allow_unknown:
            warnings.warn(msg)
        else:
            raise SystemExit("Preflight failed. " + msg)
