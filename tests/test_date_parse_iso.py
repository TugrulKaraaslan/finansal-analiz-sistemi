import pandas as pd
from utils.date_utils import parse_date


def test_parse_date_iso():
    assert parse_date("2025-03-07") == pd.Timestamp("2025-03-07")
    assert parse_date("07.03.2025") == pd.Timestamp("2025-03-07")
