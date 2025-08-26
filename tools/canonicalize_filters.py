from __future__ import annotations

import argparse
import re
from pathlib import Path

from filters.module_loader import load_filters_from_module

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
        out = re.sub(rf"\\b{re.escape(k)}\\b", v, out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", type=str, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    df = load_filters_from_module(args.module).copy()
    if "PythonQuery" in df.columns:
        df["PythonQuery"] = df["PythonQuery"].map(canonicalize_expr)
    if args.output:
        df.to_csv(args.output, sep=";", index=False)
        print(f"Canonical filters written to {args.output}")
    else:
        print(df.to_csv(sep=";", index=False))


if __name__ == "__main__":  # pragma: no cover
    main()

