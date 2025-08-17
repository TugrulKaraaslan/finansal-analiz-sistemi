from __future__ import annotations
import re, csv
from pathlib import Path
from .columns import canonicalize, ALIASES

P_UP   = re.compile(r"(\w+)_keser_(\w+)_yukari", re.I)
P_DOWN = re.compile(r"(\w+)_keser_(\w+)_asagi", re.I)
P_LVL_UP   = re.compile(r"(\w+)_keser_([0-9]+(?:\.[0-9]+)?)_?yukari", re.I)
P_LVL_DOWN = re.compile(r"(\w+)_keser_([0-9]+(?:\.[0-9]+)?)_?asagi",  re.I)

def canon_token(tok: str) -> str:
    can = ALIASES.get(canonicalize(tok), canonicalize(tok))
    return can

def tr_to_funcs(expr: str) -> str:
    s = expr.replace("<>", "!=")
    s = P_UP.sub(lambda m: f'CROSSUP("{canon_token(m.group(1))}","{canon_token(m.group(2))}")', s)
    s = P_DOWN.sub(lambda m: f'CROSSDOWN("{canon_token(m.group(1))}","{canon_token(m.group(2))}")', s)
    s = P_LVL_UP.sub(lambda m: f'CROSSOVER("{canon_token(m.group(1))}", {m.group(2)})', s)
    s = P_LVL_DOWN.sub(lambda m: f'CROSSUNDER("{canon_token(m.group(1))}", {m.group(2)})', s)
    s = re.sub(r'\b([A-Za-z_]\w*)\b', lambda m: ALIASES.get(canonicalize(m.group(1)), canonicalize(m.group(1))), s)
    return s

def compile_filters(src_csv: Path, dst_csv: Path) -> None:
    rows = []
    with src_csv.open(encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            row["PythonQuery"] = tr_to_funcs(row["PythonQuery"])
            rows.append(row)
    with dst_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["FilterCode","PythonQuery"], delimiter=";")
        w.writeheader(); w.writerows(rows)

__all__ = ["compile_filters", "tr_to_funcs"]
