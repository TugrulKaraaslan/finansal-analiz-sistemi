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


def _dataset_columns(excel_dir: Path) -> set[str]:
    xls = sorted([p for p in (excel_dir).rglob("*.xlsx")])
    assert xls, f"Preflight: Excel bulunamadı: {excel_dir}"
    df = pd.ExcelFile(xls[0]).parse(0, nrows=0)
    cols = set(map(str, df.columns))
    return cols | {c.lower() for c in cols}


def _tokens(expr: str) -> list[str]:
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or "")


def validate_filters(filters_csv: Path, excel_dir: Path) -> None:
    cols = _dataset_columns(excel_dir)
    bad: dict[str, set[str]] = {}
    alias_used: dict[str, set[str]] = {}
    with open(filters_csv, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            code = (row.get("FilterCode") or "").strip() or "<NO_CODE>"
            expr = (row.get("PythonQuery") or "").strip()
            toks = _tokens(expr)
            for t in toks:
                if t in ALIAS:
                    alias_used.setdefault(code, set()).add(f"{t}->{ALIAS[t]}")
                    continue
                if t in ALLOW_FUNCS:
                    continue
                if t not in cols:
                    bad.setdefault(code, set()).add(t)

    if alias_used:
        for k, vs in alias_used.items():
            msg = f"Preflight: legacy alias in {k}: {sorted(vs)}"
            warnings.warn(msg)

    if bad:
        msgs = [f"{k}: {sorted(v)}" for k, v in bad.items()]
        msg = "Preflight failed. Unknown tokens:\n  " + "\n  ".join(msgs)
        raise SystemExit(msg)
