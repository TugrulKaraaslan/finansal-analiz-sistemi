import argparse
import re
from pathlib import Path

import pandas as pd

from backtest.utils.names import canonical_name
from io_filters import load_filters_csv
from backtest.query_parser import SafeQuery


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".csv"}:
        return pd.read_csv(path)
    return pd.read_excel(path)


def audit_data(path: Path):
    df = _read_any(path)
    pairs = [(c, canonical_name(c)) for c in df.columns]
    print("Data columns:")
    for raw, can in pairs:
        print(f"  {raw} -> {can}")


def audit_filters(path: Path, write_fixes: bool = False):
    df = load_filters_csv(path)
    token_pat = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
    tokens = {}
    for expr in df["PythonQuery"].astype(str):
        for tok in token_pat.findall(expr):
            if tok in SafeQuery._ALLOWED_FUNCS:
                continue
            tokens[tok] = canonical_name(tok)
    print("Filter tokens:")
    for raw, can in sorted(tokens.items()):
        print(f"  {raw} -> {can}")
    if write_fixes:
        def repl(m: re.Match) -> str:
            tok = m.group(0)
            if tok in SafeQuery._ALLOWED_FUNCS:
                return tok
            return canonical_name(tok)
        df2 = df.copy()
        df2["PythonQuery"] = df2["PythonQuery"].astype(str).map(
            lambda s: token_pat.sub(repl, s)
        )
        out = path.parent / "filters_fixed.csv"
        df2.to_csv(out, index=False)
        print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=str, default="Veri", help="data file or directory")
    ap.add_argument("--filters", type=str, default="filters.csv")
    ap.add_argument("--write-fixes", action="store_true")
    args = ap.parse_args()

    data_path = Path(args.data)
    if data_path.is_dir():
        first = next(
            list(data_path.glob("*.csv")) or list(data_path.glob("*.xlsx")),
            None,
        )
        if first:
            audit_data(first)
    elif data_path.exists():
        audit_data(data_path)

    filt_path = Path(args.filters)
    if filt_path.exists():
        audit_filters(filt_path, write_fixes=args.write_fixes)


if __name__ == "__main__":
    main()
