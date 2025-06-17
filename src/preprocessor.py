import pandas as pd


def fill_missing_business_day(df: pd.DataFrame, date_col: str = "tarih") -> pd.DataFrame:
    """Shift rows with NaT in ``date_col`` to the previous business day.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing a date column.
    date_col : str, optional
        Name of the date column, by default "tarih".

    Returns
    -------
    pd.DataFrame
        DataFrame where NaT dates are replaced with the previous business day.
    """
    if date_col not in df.columns:
        return df

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    dates = df[date_col]
    next_valid = dates.fillna(method="bfill")
    prev_valid = dates.fillna(method="ffill")

    adjusted = next_valid - pd.offsets.BDay(1)
    fallback = prev_valid - pd.offsets.BDay(1)

    mask = dates.isna()
    df.loc[mask, date_col] = adjusted.where(~next_valid.isna(), fallback)[mask]
    return df
