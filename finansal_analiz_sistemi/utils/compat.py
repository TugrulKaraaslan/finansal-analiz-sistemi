"""Compatibility helpers for finansal_analiz_sistemi package."""

from __future__ import annotations


def transpose(
    df,
    axis0: int = 0,
    axis1: int = 1,
    copy: bool | None = None,
) -> "pd.DataFrame":
    """Backwards compatible helper for :meth:`DataFrame.swapaxes`.

    Parameters mimic ``swapaxes`` but only ``axis1=0`` and ``axis2=1`` are
    supported. ``copy=None`` matches the previous default behaviour of returning
    a view when possible.
    """
    if axis1 == axis2:
        return df.copy(deep=bool(copy))
    if (axis1, axis2) not in ((0, 1), ("index", "columns")):
        raise ValueError("only axes 0 and 1 are supported")
    return df.transpose(copy=False if copy is None else copy)
