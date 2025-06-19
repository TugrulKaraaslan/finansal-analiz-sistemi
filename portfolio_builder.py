import pandas as pd


def calculate_total_return(code: str, pos_df: pd.DataFrame) -> float:
    """Return weighted total return for a filter."""
    from config import cfg

    w = cfg.get("filter_weights", {}).get(code, 1.0)
    total_return = (pos_df["raw_return"] * w).sum()
    return total_return
