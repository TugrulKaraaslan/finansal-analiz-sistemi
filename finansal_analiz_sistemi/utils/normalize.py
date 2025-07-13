"""Helpers for normalizing filter CSV column names."""

import pandas as pd


def normalize_filtre_kodu(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the ``filtre_kodu`` column name.

    Possible variants like ``FilterCode`` or ``filtercode`` are converted to
    ``filtre_kodu`` after stripping surrounding whitespace. When multiple
    columns match, only the first is kept. Raises ``KeyError`` if no matching
    column exists.

    Args:
        df (pd.DataFrame): DataFrame containing a ``filtre_kodu``-like column.

    Returns:
        pd.DataFrame: DataFrame with a normalized ``filtre_kodu`` column.

    """
    # Harici müdahalelerden etkilenmemek için kopya üzerinde çalış
    out = df.copy()

    # Geçerli sütun isimlerini normalize et
    normalized = {c: c.strip().lower() for c in out.columns}

    # Aliases to be mapped to 'filtre_kodu'
    alias_map = {
        col: "filtre_kodu"
        for col, norm in normalized.items()
        if norm in {"filtercode", "filtre_kodu"}
    }

    out = out.rename(columns=alias_map)

    if "filtre_kodu" not in out.columns:
        raise KeyError("'filtre_kodu' sütunu bulunamadı – CSV başlıklarını kontrol et")

    # Aynı isimde birden fazla sütun oluştuysa ilkini sakla
    out = out.loc[:, ~out.columns.duplicated()]

    return out
