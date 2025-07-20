from datetime import date

import pandas as pd

from utils.date_utils import parse_date


def test_parse_date_handles_none_and_datetime():
    dt = pd.Timestamp("2025-03-07")
    assert parse_date(dt) == dt
    assert parse_date(None) is pd.NaT
    assert parse_date("") is pd.NaT
    assert parse_date(pd.NaT) is pd.NaT


def test_parse_date_handles_date_object():
    d = date(2025, 3, 7)
    assert parse_date(d) == pd.Timestamp("2025-03-07")
