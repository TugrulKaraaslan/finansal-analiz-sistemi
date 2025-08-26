from __future__ import annotations

"""Utility script to lint filter files.

This script loads the project configuration and determines the Excel
directory used by tests. The location can be overridden via the
``DATA_DIR`` (veya geriye dönük olarak ``EXCEL_DIR``) environment variable
which is useful in CI where fixtures are generated at runtime.
"""

import re
import sys
from pathlib import Path

import pandas as pd
import yaml

from backtest.filters.engine import ALIAS
from backtest.paths import EXCEL_DIR
from filters.module_loader import load_filters_from_module


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
    filters_module = sys.argv[2] if len(sys.argv) > 2 else None
    # fmt: on
    _load_cfg(cfg_path)

    excel_dir = EXCEL_DIR
    print(f"Using excel_dir={excel_dir}")

    sample = next(excel_dir.rglob("*.xlsx"))
    df = pd.read_excel(sample)
    cols = set(df.columns)

    fdf = load_filters_from_module(filters_module)
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
