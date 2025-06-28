import pandas as pd

from finansal_analiz_sistemi.utils import swapaxes


def test_swapaxes_basic():
    df = pd.DataFrame({"a": [1, 2]})
    out = swapaxes(df)
    pd.testing.assert_frame_equal(out, df.transpose())
