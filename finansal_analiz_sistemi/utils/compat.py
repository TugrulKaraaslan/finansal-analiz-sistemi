"""Compatibility helpers for finansal_analiz_sistemi package."""

import pandas as pd


def transpose(df: pd.DataFrame) -> pd.DataFrame:
    """swapaxes(0, 1) geçerli kalması için geriye uyumlu çözüm."""
    return df.T
