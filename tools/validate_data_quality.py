from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

import pandas as pd
import pandera as pa
import yaml
from pandera import Column, DataFrameSchema

sys.path.append(str(Path(__file__).resolve().parent.parent))

from backtest.paths import DATA_DIR  # noqa: E402

CFG = Path("contracts/data_quality.yaml")
assert CFG.exists(), "missing contracts/data_quality.yaml"
cfg = yaml.safe_load(CFG.read_text())

# Şema
req = cfg.get("required_columns", {})
schema = DataFrameSchema(
    {
        "date": Column("datetime64[ns]"),
        "open": Column(float, nullable=False),
        "high": Column(float, nullable=False),
        "low": Column(float, nullable=False),
        "close": Column(float, nullable=False),
        "volume": Column(float, nullable=False),
    },
    coerce=True,
)

# Kurallar
rules = cfg.get("rules", {})


def validate_df(df: pd.DataFrame) -> list[dict]:
    problems: list[dict] = []
    # tip/zorunlu kolon
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        for err in e.failure_cases.to_dict("records"):
            reason = f"{err.get('check')} at {err.get('column')} " f"-> {err.get('failure_case')}"
            problems.append({"type": "schema", "reason": reason})

    # date alanını üret
    is_dt = pd.api.types.is_datetime64_any_dtype
    if "date" in df.columns and not is_dt(df["date"]):
        try:
            df = df.copy()
            df["date"] = pd.to_datetime(df["date"])
        except Exception as ex:
            problems.append(
                {
                    "type": "schema",
                    "reason": f"date parse failed: {ex}",
                }
            )
            return problems

    # Mantıksal kurallar
    if rules.get("date_unique"):
        dups = df["date"].duplicated().sum()
        if dups > 0:
            problems.append(
                {
                    "type": "logic",
                    "reason": f"duplicate dates: {dups}",
                }
            )
    if rules.get("date_sorted_asc"):
        if not df["date"].is_monotonic_increasing:
            problems.append(
                {
                    "type": "logic",
                    "reason": "date not sorted ascending",
                }
            )
    if rules.get("non_negative_volume") and "volume" in df:
        if (df["volume"] < 0).any():
            problems.append(
                {
                    "type": "logic",
                    "reason": "negative volume detected",
                }
            )
    if rules.get("ohlc_bounds"):
        mn = df[["open", "close", "low", "high"]].min(axis=1)
        mx = df[["open", "close", "low", "high"]].max(axis=1)
        if (df["low"] > mn).any() or (df["high"] < mx).any():
            problems.append(
                {
                    "type": "logic",
                    "reason": "OHLC bounds violated",
                }
            )
    if rules.get("no_full_nan_rows"):
        if df.isna().all(axis=1).any():
            problems.append(
                {
                    "type": "logic",
                    "reason": "full-NaN rows present",
                }
            )

    # Toleranslar
    tol = cfg.get("tolerances", {})
    max_nan = float(tol.get("max_nan_ratio_per_column", 0.0))
    if max_nan > 0:
        ratio = df.isna().mean().max()
        if ratio > max_nan:
            reason = f"max nan ratio exceeded: {ratio:.3f} > {max_nan:.3f}"
            problems.append({"type": "tolerance", "reason": reason})

    max_dup = float(tol.get("max_duplicate_ratio", 0.0))
    if max_dup >= 0:
        # duplicate ratio tarih alanına göre
        if "date" in df.columns:
            dup_ratio = df["date"].duplicated().mean()
            if dup_ratio > max_dup:
                reason = f"duplicate ratio {dup_ratio:.3f} > {max_dup:.3f}"
                problems.append({"type": "tolerance", "reason": reason})

    return problems


# Hedef dosyalar
includes = cfg.get("include") or ["**/*.xlsx"]
excludes = cfg.get("exclude") or []


def should_include(p: Path) -> bool:
    s = str(p)
    inc = (
        any(
            Path(DATA_DIR, "").joinpath(p).match(pattern) or fnmatch.fnmatch(s, pattern)
            for pattern in includes
        )
        if includes
        else True
    )

    def _match(pattern: str) -> bool:
        path = Path(DATA_DIR, "").joinpath(p)
        return path.match(pattern) or fnmatch.fnmatch(s, pattern)

    exc = any(_match(pattern) for pattern in excludes)
    return inc and not exc


files = [Path(p) for p in DATA_DIR.rglob("*.xlsx") if should_include(p)]

report = {"root": str(DATA_DIR), "files": []}
for f in files:
    try:
        # İlk sheet
        df = pd.ExcelFile(f).parse(0)
        probs = validate_df(df)
        report["files"].append({"file": str(f.relative_to(DATA_DIR)), "problems": probs})
    except Exception as e:
        report["files"].append(
            {
                "file": str(f.relative_to(DATA_DIR)),
                "problems": [{"type": "io", "reason": str(e)}],
            }
        )

out_dir = Path("artifacts/quality")
out_dir.mkdir(parents=True, exist_ok=True)
(Path(out_dir / "report.json")).write_text(
    json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
)

# Konsol özeti
criticals = []
warnings = []
for item in report["files"]:
    for p in item["problems"]:
        if p["type"] in {"schema", "logic"}:
            criticals.append((item["file"], p["reason"]))
        else:
            warnings.append((item["file"], p["reason"]))

if warnings:
    print("WARNINGS:")
    for w in warnings:
        print(" -", w[0], "→", w[1])

if criticals:
    print("CRITICALS:")
    for c in criticals:
        print(" -", c[0], "→", c[1])
    raise SystemExit(2)

print("data quality validation passed")
