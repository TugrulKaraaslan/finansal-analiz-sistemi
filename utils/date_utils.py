import pandas as pd
from datetime import datetime


def parse_date(date_str: str) -> datetime:
    """'2025-03-07' -> ISO   |  '07.03.2025' -> TR  | raise ValueError."""
    try:
        return pd.to_datetime(date_str, format="%d.%m.%Y")
    except ValueError:
        try:
            return pd.to_datetime(date_str, format="%Y-%m-%d")
        except ValueError:
            return pd.to_datetime(date_str, dayfirst=True, errors="raise")
