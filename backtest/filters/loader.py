from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger("backtest")


def sanitize_filters_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize placeholder expressions in *df*.

    - Boolean literals (``true``/``false``) are allowed but a warning is logged.
    - Empty expressions are dropped entirely – nothing to evaluate.
    """

    if "PythonQuery" not in df.columns:
        return df

    exprs = df["PythonQuery"].astype(str)

    # Drop rows with empty expressions. We choose to drop instead of keeping
    # disabled rows because there is no "enabled" flag in the schema.
    mask_empty = exprs.str.strip().eq("")
    if mask_empty.any():
        df = df.loc[~mask_empty].copy()

    mask_bool = exprs.str.strip().str.lower().isin({"true", "false"})
    if mask_bool.any():
        ids = df.loc[mask_bool, "FilterCode"].astype(str).tolist()
        for fid in ids:
            log.warning("expr boolean literal; id=%s", fid)

    return df


__all__ = ["sanitize_filters_df"]

