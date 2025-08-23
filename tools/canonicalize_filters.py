import csv
import re
import sys
from pathlib import Path

ALIAS = {
    "its_9": "ichimoku_conversionline",
    "iks_26": "ichimoku_baseline",
    "macd_12_26_9": "macd_line",
    "macds_12_26_9": "macd_signal",
    "bbm_20 2": "bbm_20_2",
    "bbu_20 2": "bbu_20_2",
    "bbl_20 2": "bbl_20_2",
}


def canonicalize_expr(expr: str) -> str:
    out = expr or ""
    for k, v in sorted(ALIAS.items(), key=lambda x: -len(x[0])):
        out = re.sub(rf"\b{re.escape(k)}\b", v, out)
    return out


src = Path(sys.argv[1] if len(sys.argv) > 1 else "filters.csv")
dst = Path(sys.argv[2] if len(sys.argv) > 2 else "filters_canonical.csv")
rows = list(csv.DictReader(open(src, encoding="utf-8"), delimiter=";"))
for r in rows:
    r["PythonQuery"] = canonicalize_expr(r.get("PythonQuery", ""))
with open(dst, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"Canonical filters written to {dst}")
