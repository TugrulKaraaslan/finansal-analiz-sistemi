# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
"""CSV validation helpers for filter definitions.

The expected structure for filter definition files is::

    FilterCode;PythonQuery;Group

Where ``Group`` is optional and may be omitted. ``FilterCode`` and
``PythonQuery`` must be non-empty strings.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

try:  # Pandera import may vary by version
    import pandera as pa
except Exception as exc:  # pragma: no cover - import error path
    raise ImportError(
        "Pandera is required for filter validation. Install with 'pip install pandera'."
    ) from exc


_SCHEMA = pa.DataFrameSchema(
    {
        "FilterCode": pa.Column(
            pa.String, nullable=False, checks=pa.Check.str_length(min_value=1)
        ),
        "PythonQuery": pa.Column(
            pa.String, nullable=False, checks=pa.Check.str_length(min_value=1)
        ),
        "Group": pa.Column(pa.String, nullable=True, required=False),
    },
    coerce=True,
)


def validate_filters(path: str | Path) -> pd.DataFrame:
    """Validate filter definitions CSV against the schema.

    The file must contain ``FilterCode`` and ``PythonQuery`` columns and may
    include an optional ``Group`` column.
    """
    p = Path(path)
    df = pd.read_csv(p, sep=None, engine="python")
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
