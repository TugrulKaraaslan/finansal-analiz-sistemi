"""Helpers for reading filter CSV files."""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from utils.paths import resolve_path

REQUIRED_COLUMNS = {"FilterCode", "PythonQuery"}


def load_filters_csv(path: str | Path) -> pd.DataFrame:
    """Load filters from CSV with validation and basic normalization.

    Parameters
    ----------
    path:
        Location of the CSV file.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the filter definitions. If the file is missing
        or cannot be parsed, an empty DataFrame is returned and a warning is
        issued. Missing required columns raise ``RuntimeError``.
    """

    p = resolve_path(path)
    if not p.exists():
        warnings.warn(f"Filters CSV bulunamadı: {p}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(p, encoding="utf-8")
    except Exception:
        warnings.warn(f"Filters CSV okunamadı: {p}")
        return pd.DataFrame()

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise RuntimeError(
            "Eksik kolon(lar): " + ", ".join(sorted(missing))
        )

    # basic normalization
    df["FilterCode"] = df["FilterCode"].astype(str).str.strip()
    df["PythonQuery"] = df["PythonQuery"].astype(str)
    return df


__all__ = ["load_filters_csv"]

