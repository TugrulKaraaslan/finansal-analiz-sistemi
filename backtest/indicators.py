from __future__ import annotations

import logging
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def compute_indicators(
    df: pd.DataFrame,
    params: Optional[Dict[str, List[int]]] = None,
    *,
    engine: str = "none",
) -> pd.DataFrame:
    """Return the input DataFrame without computing indicators.

    Parameters
    ----------
    df : pandas.DataFrame
        Input price data.
    params : dict, optional
        Unused placeholder for compatibility.
    engine : str, default "none"
        Must always be ``"none"``. Any other value raises ``ValueError``.

    Returns
    -------
    pandas.DataFrame
        The original DataFrame (no copy).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")
    if params is not None and not isinstance(params, dict):
        raise TypeError("params must be a dict or None")
    if engine != "none":
        raise ValueError(
            "Gösterge hesaplaması politika gereği devre dışı (engine='none')."
        )
    logger.info("indicators: engine=none (policy lock), no computation")
    return df
