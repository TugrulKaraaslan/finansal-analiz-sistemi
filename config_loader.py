"""Load configuration data used for indicator calculations.

This module exposes helpers for extracting crossover names from filter
files and configuration lists.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from finansal_analiz_sistemi import config

# Regex to capture any crossover column name
CROSSOVER_NAME_RE = re.compile(r"([A-Za-z0-9_]+_keser_[A-Za-z0-9_]+_(?:yukari|asagi))")
EMA_CLOSE_RE = re.compile(r"ema_(\d+)_keser_close_(yukari|asagi)")


@lru_cache(maxsize=1)
def load_crossover_names(csv_path: str | Path | None = None) -> list[str]:
    """Return crossover column names referenced by filters and config.

    Parameters
    ----------
    csv_path : str or Path, optional
        Filter CSV file. Defaults to ``config.FILTRE_DOSYA_YOLU``.

    Returns
    -------
    list[str]
        Sorted list of unique crossover column names.

    """
    path = Path(csv_path or config.FILTRE_DOSYA_YOLU)
    names: set[str] = set()
    try:
        df = pd.read_csv(path, sep=";", engine="python")
    except Exception:
        df = pd.DataFrame()
    if "PythonQuery" in df.columns:
        for expr in df["PythonQuery"].dropna().astype(str):
            names.update(CROSSOVER_NAME_RE.findall(expr))
    for _, _, above, below in getattr(config, "SERIES_SERIES_CROSSOVERS", []):
        names.update([above, below])
    for col, _, suff in getattr(config, "SERIES_VALUE_CROSSOVERS", []):
        suf = str(suff).replace(".", "p")
        names.update([f"{col}_keser_{suf}_yukari", f"{col}_keser_{suf}_asagi"])
    return sorted(names)


def load_ema_close_crossovers(csv_path: str | Path | None = None) -> list[str]:
    """Return crossover names matching ``ema_N_keser_close_*``.

    Parameters
    ----------
    csv_path : str or Path, optional
        Optional filter CSV path passed to :func:`load_crossover_names`.

    Returns
    -------
    list[str]
        Sorted list of EMA-close crossover column names.

    """
    return [n for n in load_crossover_names(csv_path) if EMA_CLOSE_RE.fullmatch(n)]
