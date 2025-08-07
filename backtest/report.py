from __future__ import annotations

import warnings
from pathlib import Path
from typing import Union

import pandas as pd

from utils.paths import resolve_path


def drop_inactive_filters(df_stats: pd.DataFrame, out_dir: Union[str, Path] = "raporlar") -> pd.DataFrame:
    """Remove filters with zero trades from stats and log them.

    Parameters
    ----------
    df_stats : pd.DataFrame
        Statistics per filter. Must contain ``FilterCode`` and ``trade_count`` columns.
    out_dir : str | Path, default "raporlar"
        Directory where ``inactive_filters.txt`` will be written.

    Returns
    -------
    pd.DataFrame
        ``df_stats`` without rows where ``trade_count`` equals zero.
    """
    if not isinstance(df_stats, pd.DataFrame):
        raise TypeError("df_stats must be a DataFrame")

    required_cols = {"FilterCode", "trade_count"}
    missing = required_cols.difference(df_stats.columns)
    if missing:
        raise ValueError(f"df_stats missing columns: {', '.join(sorted(missing))}")

    mask = df_stats["trade_count"] == 0
    inactive = df_stats.loc[mask, "FilterCode"].astype(str).tolist()

    if inactive:
        out_path = resolve_path(out_dir) / "inactive_filters.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            fh.write("\n".join(inactive))
        warnings.warn(
            f"{len(inactive)} filtre işlem üretmedi: {', '.join(inactive)}",
            RuntimeWarning,
        )

    return df_stats.loc[~mask].copy()


__all__ = ["drop_inactive_filters"]
