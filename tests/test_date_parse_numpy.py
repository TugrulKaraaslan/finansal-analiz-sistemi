import numpy as np
import pandas as pd

from utils.date_utils import parse_date


def test_parse_date_numpy_datetime64():
    ts = parse_date(np.datetime64("2025-03-07"))
    assert ts == pd.Timestamp("2025-03-07")
