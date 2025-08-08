# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
"""Helpers for reading filter CSV files.

Filter definition files are expected to contain ``FilterCode`` and
``PythonQuery`` columns and may include an optional ``Group`` column.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.paths import resolve_path

REQUIRED_COLUMNS = {"FilterCode", "PythonQuery"}


def load_filters_csv(path: str | Path) -> pd.DataFrame:
    """Load filters from CSV with validation and basic normalization.

    The CSV must define ``FilterCode`` and ``PythonQuery`` columns. ``Group`` is
    optional and ignored if absent.

    Parameters
    ----------
    path:
        Location of the CSV file.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the filter definitions. If the file is missing,
        ``FileNotFoundError`` is raised. CSV parse issues raise
        ``RuntimeError``. Missing required columns raise ``RuntimeError``.
    """

    p = resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"Filters CSV bulunamadı: {p}")
    try:
        df = pd.read_csv(p, encoding="utf-8", sep=None, engine="python")
    except Exception as exc:
        raise RuntimeError(f"Filters CSV parse edilemedi: {p}") from exc

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise RuntimeError("Eksik kolon(lar): " + ", ".join(sorted(missing)))

    # basic normalization
    df["FilterCode"] = df["FilterCode"].astype(str).str.strip()
    df["PythonQuery"] = df["PythonQuery"].astype(str)
    dups = df["FilterCode"][df["FilterCode"].duplicated()]
    if not dups.empty:
        dup_codes = ", ".join(sorted(dups.unique()))
        raise RuntimeError(f"Duplicate FilterCode detected: {dup_codes}")
    return df


__all__ = ["load_filters_csv"]
