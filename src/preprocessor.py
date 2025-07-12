"""Minimal preprocessing utilities used by the CLI helpers."""

import pandas as pd


def fill_missing_business_day(
    df: pd.DataFrame, date_col: str = "tarih"
) -> pd.DataFrame:
    """Replace ``NaT`` values with the previous business day.

    Rows with missing dates are shifted backward so every entry aligns with a
    valid trading day.

    Args:
        df (pd.DataFrame): Input DataFrame containing a date column.
        date_col (str, optional): Name of the date column. Defaults to
            ``"tarih"``.

    Returns:
        pd.DataFrame: DataFrame where missing dates are backfilled with the
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
    next_valid = dates.bfill()
    if next_valid.isna().any():
        next_valid = next_valid.fillna(dates.ffill())

    # determine how far each NaT is from the next valid date
    offsets = []
    counter = 0
    for is_na in reversed(mask.to_list()):
        if is_na:
            counter += 1
            offsets.append(counter)
        else:
            offsets.append(0)
            counter = 0
    offsets = list(reversed(offsets))

    adjusted = next_valid.copy()
    for idx, off in enumerate(offsets):
        if off:
            adjusted.iloc[idx] = adjusted.iloc[idx] - pd.offsets.BDay(off)

    df.loc[mask, date_col] = adjusted[mask]
    return df
