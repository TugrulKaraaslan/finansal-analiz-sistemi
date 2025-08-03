"""Load configuration data used for indicator calculations.

This module exposes helpers for extracting crossover names from filter
files and configuration lists.
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd
from finansal_analiz_sistemi import config

__all__ = [
    "load_crossover_names",
    "load_ema_close_crossovers",
    "clear_cache",
]

# Regex to capture any crossover column name
CROSSOVER_NAME_RE = re.compile(r"([A-Za-z0-9_]+_keser_[A-Za-z0-9_]+_(?:yukari|asagi))")
EMA_CLOSE_RE = re.compile(r"ema_(\d+)_keser_close_(yukari|asagi)")


@lru_cache(maxsize=1)
def load_crossover_names(
    csv_path: str | Path | None = None,
    *,
    encoding: str = "utf-8",
) -> list[str]:
    """Return crossover column names referenced by filters and config.

    Args:
        csv_path (str | Path, optional): Filter CSV file. Defaults to
            :data:`config.FILTRE_DOSYA_YOLU`.
        encoding (str, optional): Character set used when reading the CSV
            file. ``"utf-8"`` by default.

    Returns:
        list[str]: Sorted list of unique crossover column names.

    """
    path = Path(csv_path or config.FILTRE_DOSYA_YOLU)
    names: set[str] = set()
    try:
        df = pd.read_csv(path, sep=";", engine="python", encoding=encoding)
    except Exception as exc:
        logging.getLogger(__name__).warning("Filter CSV '%s' okunamadı: %s", path, exc)
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


@lru_cache(maxsize=1)
def load_ema_close_crossovers(
    csv_path: str | Path | None = None,
    *,
    encoding: str = "utf-8",
) -> list[str]:
    """Return crossover names matching ``ema_N_keser_close_*``.

    Args:
        csv_path (str | Path, optional): Optional filter CSV path forwarded to
            :func:`load_crossover_names`.
        encoding (str, optional): Character set used when reading the CSV
            file. ``"utf-8"`` by default.

    Returns:
        list[str]: Sorted list of EMA-close crossover column names.

    """
    return [
        n
        for n in load_crossover_names(csv_path, encoding=encoding)
        if EMA_CLOSE_RE.fullmatch(n)
    ]


def clear_cache() -> None:
    """Clear cached results of :func:`load_crossover_names` and
    :func:`load_ema_close_crossovers`."""
    load_crossover_names.cache_clear()
    load_ema_close_crossovers.cache_clear()
