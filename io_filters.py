"""Helpers for reading filter CSV files.

Filter definition files are expected to contain ``FilterCode`` and
``PythonQuery`` columns and may include an optional ``Group`` column.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.paths import resolve_path

REQUIRED_COLUMNS = {"FilterCode", "PythonQuery"}


def read_filters_smart(path: str | Path) -> pd.DataFrame:
    """Read ``filters.csv`` with strict delimiter but allow fallback detection.

    Primarily attempts to read using semicolon delimiter and UTF-8 encoding. If
    that fails (e.g., old files using commas), a second attempt with delimiter
    inference is made using the Python engine.
    """

    try:
        return pd.read_csv(path, sep=";", encoding="utf-8")
    except Exception:
        return pd.read_csv(path, sep=None, engine="python", encoding="utf-8")


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
        df = read_filters_smart(p)
    except Exception as exc:
        raise RuntimeError(f"Filters CSV parse edilemedi: {p}") from exc

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise RuntimeError("Eksik kolon(lar): " + ", ".join(sorted(missing)))

    # basic normalization and emptiness checks
    df["FilterCode"] = df["FilterCode"].fillna("").astype(str).str.strip()
    df["PythonQuery"] = df["PythonQuery"].fillna("").astype(str).str.strip()
    if df["FilterCode"].eq("").any():
        raise RuntimeError("FilterCode boş olamaz")
    if df["PythonQuery"].eq("").any():
        raise RuntimeError("PythonQuery boş olamaz")
    dups = df["FilterCode"][df["FilterCode"].duplicated()]
    if not dups.empty:
        dup_codes = ", ".join(sorted(dups.unique()))
        raise RuntimeError(f"Duplicate FilterCode detected: {dup_codes}")
    return df


__all__ = ["load_filters_csv", "read_filters_smart"]
