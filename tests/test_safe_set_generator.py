import pandas as pd

from finansal.utils import safe_set


def test_safe_set_accepts_generator():
    df = pd.DataFrame({"close": [1, 2, 3]})
    values = (v * 2 for v in range(2))
    safe_set(df, "foo", values)
    assert list(df["foo"])[:2] == [0, 2]
    assert pd.isna(df["foo"].iloc[2])
