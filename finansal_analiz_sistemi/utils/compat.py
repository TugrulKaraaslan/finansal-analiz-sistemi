"""Compatibility helpers for finansal_analiz_sistemi package."""

from __future__ import annotations

import pandas as pd


def transpose(
    df: pd.DataFrame, axis0: int = 0, axis1: int = 1, copy: bool | None = None
) -> pd.DataFrame:
    """Transpose ``df`` while mimicking ``DataFrame.swapaxes``.

    Only ``axis0=0`` and ``axis1=1`` are supported. ``copy=None`` preserves the
    original view when possible.

    Args:
        df (pd.DataFrame): Frame to transpose.
        axis0 (int, optional): Source axis. Defaults to ``0``.
        axis1 (int, optional): Destination axis. Defaults to ``1``.
        copy (bool | None, optional): Whether to copy the data. ``None``
            replicates the legacy behavior of returning a view when possible.

    Returns:
        pd.DataFrame: Transposed DataFrame.
    """
    if axis0 == axis1:
        return df.copy(deep=bool(copy))

    valid_pairs = {
        (0, 1),
        (1, 0),
        ("index", "columns"),
        ("columns", "index"),
    }
    if (axis0, axis1) not in valid_pairs:
        raise ValueError("only axes 0 and 1 are supported")

    return df.transpose(copy=False if copy is None else copy)
