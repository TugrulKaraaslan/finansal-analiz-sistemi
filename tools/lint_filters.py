from __future__ import annotations

"""Utility script to lint filter files.

This script loads the project configuration and determines the Excel
directory used by tests. The location can be overridden via the
``EXCEL_DIR`` environment variable which is useful in CI where fixtures are
generated at runtime.
"""

from pathlib import Path
import os
import sys
import yaml
import re
import pandas as pd
from backtest.filters.engine import ALIAS


def _load_cfg(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _tokenize(expr: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr))
    for alias in ALIAS:
        if " " in alias and alias in expr:
            tokens.add(alias)
    return tokens


def main() -> None:
    # fmt: off
    cfg_path = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config_scan.yml")
    )
    filters_path = (
        Path(sys.argv[2]) if len(sys.argv) > 2 else Path("filters.csv")
    )
    # fmt: on
    cfg = _load_cfg(cfg_path)

    # mevcut cfg okuma mantığının üstüne ENV override ekle
    excel_dir = Path(os.getenv("EXCEL_DIR", cfg["data"]["excel_dir"]))
    print(f"Using excel_dir={excel_dir}")

    sample = next(excel_dir.rglob("*.xlsx"))
    df = pd.read_excel(sample)
    cols = set(df.columns)

    fdf = pd.read_csv(
        filters_path,
        sep=";",
        usecols=["FilterCode", "PythonQuery"],
        dtype=str,
    )
    ok = True
    for i, expr in enumerate(fdf.get("PythonQuery", [])):
        tokens = _tokenize(str(expr))
        tokens -= {
            "and",
            "or",
            "not",
            "True",
            "False",
            "cross_up",
            "cross_down",
        }
        missing = [t for t in tokens if ALIAS.get(t, t) not in cols]
        if missing:
            msg = ", ".join(sorted(missing))
            print(f"Row {i}: unknown columns {msg}")
            ok = False
    if not ok:
        sys.exit(1)
    print("OK")


if __name__ == "__main__":  # pragma: no cover
    main()
