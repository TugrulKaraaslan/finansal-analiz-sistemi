"""Compatibility helpers for finansal_analiz_sistemi package."""

import pandas as pd

def transpose(df: pd.DataFrame, axis0: int = 0, axis1: int = 1, copy: bool | None = None) -> pd.DataFrame:
    """Backwards compatible helper for :meth:`DataFrame.swapaxes`.

    Parameters mimic ``swapaxes`` but only ``axis0=0`` and ``axis1=1`` are
    supported. ``copy=None`` matches the previous default behaviour of returning
    a view when possible.
    """
    if axis0 == axis1:
        return df.copy(deep=bool(copy))
    if (axis0, axis1) not in ((0, 1), ("index", "columns")):
        raise ValueError("only axes 0 and 1 are supported")
    return df.transpose(copy=False if copy is None else copy)
