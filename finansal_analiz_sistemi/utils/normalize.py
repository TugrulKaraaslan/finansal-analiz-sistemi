"""Normalize column names used in filter CSV files.

Utilities here ensure variants like ``FilterCode`` or ``filtercode`` are
mapped to the canonical ``filtre_kodu`` label before processing.
"""

from __future__ import annotations

import pandas as pd


def normalize_filtre_kodu(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the ``filtre_kodu`` column name.

    Possible variants like ``FilterCode`` or ``filtercode`` are converted to
    ``filtre_kodu`` after stripping surrounding whitespace. Aliases containing
    spaces or underscores are also recognized. When multiple
    columns match, only the first is kept. Raises ``KeyError`` if no matching
    column exists.

    Args:
        df (pd.DataFrame): DataFrame containing a ``filtre_kodu``-like column.

    Returns:
        pd.DataFrame: DataFrame with a normalized ``filtre_kodu`` column.

    """
    # Work on a copy to avoid external side effects
    out = df.copy()

    # Geçerli sütun isimlerini normalize et
    normalized = {c: c.strip().lower() for c in out.columns}

    # Aliases to be mapped to 'filtre_kodu'
    alias_map = {}
    for col, norm in normalized.items():
        key = norm.replace(" ", "").replace("_", "")
        if key in {"filtercode", "filtrekodu"}:
            alias_map[col] = "filtre_kodu"

    out = out.rename(columns=alias_map)

    if "filtre_kodu" not in out.columns:
        raise KeyError("'filtre_kodu' sütunu bulunamadı – CSV başlıklarını kontrol et")

    # Aynı isimde birden fazla sütun oluştuysa ilkini sakla
    out = out.loc[:, ~out.columns.duplicated()]

    return out
