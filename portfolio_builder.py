import pandas as pd


def calculate_total_return(code: str, pos_df: pd.DataFrame) -> float:
    """Return weighted total return for a filter.

    Missing or non-numeric values are treated as ``0`` and a missing
    ``raw_return`` column results in ``0.0``.
    """

    from finansal_analiz_sistemi.config import cfg

    weight = float(cfg.get("filter_weights", {}).get(code, 1.0))

    raw_col = pos_df.get("raw_return")
    if raw_col is None:
        return 0.0

    raw = pd.to_numeric(raw_col, errors="coerce")
    total_return = (raw.fillna(0) * weight).sum()
    return float(total_return)
