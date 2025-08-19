from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_filters(path: str) -> pd.DataFrame:
    """Load filter definitions from a CSV file.

    Parameters
    ----------
    path:
        Location of the CSV file.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the filter definitions.
    """

    p = Path(path)
    return pd.read_csv(p, encoding="utf-8", sep=",")


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to CSV with UTF-8 encoding."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8")


__all__ = ["load_filters", "save_csv"]

