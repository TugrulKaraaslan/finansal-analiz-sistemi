#!/usr/bin/env python3
from __future__ import annotations
import re
import argparse
import sys
from pathlib import Path
import pandas as pd

RE_PSAR = re.compile(r"\bpsarl_0\.02_0\.2\b", flags=re.IGNORECASE)
RE_WILLR = re.compile(r"(?<![A-Za-z0-9_])_(100|80|70|50)\b", flags=re.IGNORECASE)
RE_EQ = re.compile(r"\s=\s=")
RE_CCI = re.compile(r"\bcci_(\d+)_0\b", flags=re.IGNORECASE)
RE_AROONU = re.compile(r"\baroonu_(\d+)\b", flags=re.IGNORECASE)
RE_AROOND = re.compile(r"\baroond_(\d+)\b", flags=re.IGNORECASE)
RE_CLASSICP = re.compile(r"\s*&\s*[^&]*classicpivots_1h_p[^&]*", flags=re.IGNORECASE)


def fix_expr(expr: str) -> str:
    s = expr
    s = RE_PSAR.sub("psarl_0_02_0_2", s)
    s = RE_WILLR.sub(lambda m: f"-{m.group(1)}", s)
    s = RE_EQ.sub("==", s)
    s = re.sub(r"\s*==\s*", " == ", s)
    s = RE_CCI.sub(lambda m: f"cci_{m.group(1)}", s)
    s = RE_AROONU.sub(lambda m: f"aroon_up_{m.group(1)}", s)
    s = RE_AROOND.sub(lambda m: f"aroon_down_{m.group(1)}", s)
    s = re.sub(r"change_1h_percent", "change_1d_percent", s, flags=re.IGNORECASE)
    s = RE_CLASSICP.sub("", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--inplace", action="store_true")
    args = p.parse_args(argv)
    path = Path(args.file)
    df = pd.read_csv(path, sep=";", dtype=str)
    df["PythonQuery"] = df["PythonQuery"].map(fix_expr)
    if args.inplace:
        df.to_csv(path, sep=";", index=False)
    else:
        df.to_csv(sys.stdout, index=False)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
