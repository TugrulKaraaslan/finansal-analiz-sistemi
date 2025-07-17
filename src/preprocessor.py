"""Utility functions for lightweight data preprocessing.

These helpers adjust date columns and remove invalid rows before
indicator calculation.
"""

import pandas as pd


def fill_missing_business_day(
    df: pd.DataFrame, date_col: str = "tarih"
) -> pd.DataFrame:
    """Backfill ``NaT`` rows with the preceding business day.

    Missing dates are shifted backward so each record aligns with a valid
    trading day according to :class:`pandas.offsets.BDay`.

    Args:
        df (pd.DataFrame): Input DataFrame containing a date column.
        date_col (str, optional): Name of the date column. Defaults to
            ``"tarih"``.

    Returns:
        pd.DataFrame: Frame where missing dates are replaced with the
        prior business day.
    """
    if date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    dates = df[date_col]
    mask = dates.isna()
    if not mask.any():
        return df

    # propagate next valid dates downward so NaT values have a reference point
    next_valid = dates.bfill().ffill()

    rev_mask = mask.iloc[::-1]
    groups = rev_mask.ne(rev_mask.shift()).cumsum()
    offset_rev = rev_mask.groupby(groups).cumcount().add(1).where(rev_mask, 0)
    offsets = offset_rev.iloc[::-1]

    adjusted = next_valid.copy()
    for idx, off in offsets[mask].items():
        if off:
            adjusted.iloc[idx] = adjusted.iloc[idx] - pd.offsets.BDay(off)

    df.loc[mask, date_col] = adjusted[mask]
    return df
