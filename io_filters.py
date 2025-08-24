"""Helpers for reading filter CSV files with a single ``;`` delimiter."""

from __future__ import annotations

from pathlib import Path
import collections

import pandas as pd
from loguru import logger

from utils.paths import resolve_path

REQUIRED_HEADER = ["FilterCode", "PythonQuery"]


def _check_delimiter(path: Path) -> None:
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    if "," in first_line and ";" not in first_line:
        raise ValueError(
            "CSV delimiter ';' bekleniyor. Lütfen dosyayı ';' ile kaydedin."
        )


def validate_filters_df(df: pd.DataFrame) -> pd.DataFrame:
    """Validate filter DataFrame ensuring strict schema and content."""

    if list(df.columns) != REQUIRED_HEADER:
        raise ValueError(f"filters.csv kolonları {REQUIRED_HEADER!r} olmalı")

    df = df.dropna(how="all")

    if df["FilterCode"].isna().any() or df["FilterCode"].astype(str).str.strip().eq("").any():
        raise ValueError("FilterCode boş olamaz")
    if df["PythonQuery"].isna().any() or df["PythonQuery"].astype(str).str.strip().eq("").any():
        raise ValueError("PythonQuery boş olamaz")

    df["FilterCode"] = df["FilterCode"].astype(str).str.strip()
    df["PythonQuery"] = df["PythonQuery"].astype(str).str.strip()

    dups = df["FilterCode"][df["FilterCode"].duplicated()]
    if not dups.empty:
        dup_codes = ", ".join(sorted(dups.unique()))
        raise ValueError(f"Duplicate FilterCode detected: {dup_codes}")
    return df


def read_filters_csv(path: Path | str) -> pd.DataFrame:
    """Read filter definitions using strict ``;`` separated schema."""

    p = resolve_path(path)
    _check_delimiter(p)
    df = pd.read_csv(p, sep=";", dtype=str, encoding="utf-8")
    return validate_filters_df(df)


def load_filters_csv(paths: list[Path | str]) -> list[dict]:
    """Load filters from multiple CSV files.

    Each path is validated via :func:`read_filters_csv`. Duplicate
    ``FilterCode`` values across files raise ``ValueError``.
    """

    all_rows: list[dict] = []
    for path in paths:
        p = resolve_path(path)
        if not p.exists():
            msg = (
                f"Filters CSV bulunamadı: {p}. "
                "'--filters-csv' ile yol belirtin veya "
                "config'te 'data.filters_csv' ayarını kontrol edin."
            )
            logger.error(msg)
            raise FileNotFoundError(msg)
        df = read_filters_csv(p)
        all_rows.extend(df.to_dict("records"))

    codes = [r["FilterCode"] for r in all_rows]
    dup = [c for c, cnt in collections.Counter(codes).items() if cnt > 1]
    if dup:
        dup_codes = ", ".join(sorted(dup))
        raise ValueError(f"Duplicate FilterCode detected across files: {dup_codes}")
    return all_rows


__all__ = ["read_filters_csv", "load_filters_csv", "validate_filters_df"]
