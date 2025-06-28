"""Compatibility helpers for finansal_analiz_sistemi package."""

import pandas as pd


def transpose(df: pd.DataFrame, *, copy: bool | None = None) -> pd.DataFrame:
    """Replacement for ``DataFrame.swapaxes(0, 1)``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to transpose.
    copy : bool | None, default None
        Whether to return a copy. ``None`` mimics the default behaviour of
        ``DataFrame.swapaxes`` which copies unless ``copy`` is explicitly
        set to ``False``.

    Returns
    -------
    pandas.DataFrame
        The transposed DataFrame.
    """

    if copy is None:
        copy = True

    return df.transpose(copy=copy)
