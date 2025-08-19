from __future__ import annotations

import pandas as pd


def make_price_frame(n: int = 10) -> pd.DataFrame:
    """Return a deterministic price DataFrame.

    Parameters
    ----------
    n:
        Number of rows. Defaults to 10.
    """
    seq = list(range(1, n + 1))
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "open": seq,
            "high": seq,
            "low": seq,
            "close": seq,
            "volume": seq,
            "EMA_10": seq,
            "RSI_14": seq,
            "relative_volume": seq,
            "BBM_20_2.0": seq,
            "BBU_20_2.1": seq,
        }
    )
    return df
