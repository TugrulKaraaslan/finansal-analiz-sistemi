"""Compatibility helpers for finansal_analiz_sistemi package."""

import pandas as pd


def transpose(df: pd.DataFrame, axis1: int = 0, axis2: int = 1) -> pd.DataFrame:
    """Compat replacement for ``DataFrame.swapaxes``.

    Pandas 3 removed :meth:`DataFrame.swapaxes`.  ``df.T`` mirrors
    ``df.swapaxes(0, 1)`` so we only support that case.  ``axis1`` and
    ``axis2`` parameters are accepted for API compatibility and must both be
    ``0`` and ``1`` respectively.  Any other values raise ``NotImplementedError``
    to signal unsupported use.
    """

    if axis1 != 0 or axis2 != 1:
        raise NotImplementedError("only axes (0, 1) are supported")
    return df.T
