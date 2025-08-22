from __future__ import annotations
import pandas as pd
from pathlib import Path


def load_benchmark(
    path: str, *, date_col: str = "date", close_col: str = "close"
) -> pd.Series:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"SM001: benchmark yok: {p}")
    if p.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p)
    if date_col not in df.columns or close_col not in df.columns:
        raise ValueError("SM001: benchmark kolonları eksik (date/close)")
    s = pd.to_datetime(df[date_col])
    out = pd.Series(df[close_col].astype(float).values, index=s)
    out = out.sort_index()
    return out
