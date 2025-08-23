#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from backtest.filters.normalize_expr import normalize_expr


def lint_file(path: str | Path, inplace: bool = False) -> int:
    """Normalize PythonQuery expressions in *path*.

    Returns the number of modified rows.  If ``inplace`` is False and
    modifications are needed, they are reported to stdout and the original
    file is left untouched.  When ``inplace`` is True the file is rewritten with
    the normalised expressions.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(path, sep=";", dtype=str)
    if "PythonQuery" not in df.columns:
        raise SystemExit("PythonQuery column missing")

    norm = df["PythonQuery"].map(lambda s: normalize_expr(s)[0])
    changed = norm != df["PythonQuery"]
    n_changed = int(changed.sum())
    if n_changed and not inplace:
        for idx in df.index[changed]:
            old = df.at[idx, "PythonQuery"]
            new = norm.iloc[idx]
            print(f"{idx}: {old} -> {new}")
    if inplace and n_changed:
        df["PythonQuery"] = norm
        df.to_csv(path, sep=";", index=False)
    return n_changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Normalize filters CSV")
    p.add_argument("file", help="CSV file path")
    p.add_argument("--inplace", action="store_true", help="Rewrite file in-place")
    args = p.parse_args(argv)
    changed = lint_file(args.file, inplace=args.inplace)
    return 0 if changed == 0 or args.inplace else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
