# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
"""CSV validation helpers."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera as pa


_SCHEMA = pa.DataFrameSchema(
    {
        "filter_name": pa.Column(pa.String, nullable=False, checks=pa.Check.str_length(min_value=1)),
        "query": pa.Column(pa.String, nullable=False, checks=pa.Check.str_length(min_value=1)),
        "group": pa.Column(pa.String, nullable=True),
    },
    coerce=True,
)


def validate_filters(path: str | Path) -> pd.DataFrame:
    """Validate filter definitions CSV against the schema."""
    p = Path(path)
    df = pd.read_csv(p)
    try:
        _SCHEMA.validate(df, lazy=True)
    except pa.errors.SchemaErrors as err:
        fc = err.failure_cases
        if not fc.empty and fc["index"].notna().any():
            first = fc[fc["index"].notna()].iloc[0]
            column = first["column"]
            row_num = int(first["index"]) + 2
            raise ValueError(f"{p.name} satır {row_num} – {column} boş olamaz") from None
        raise ValueError(f"{p.name} şema doğrulaması başarısız") from None
    return df


__all__ = ["validate_filters"]
