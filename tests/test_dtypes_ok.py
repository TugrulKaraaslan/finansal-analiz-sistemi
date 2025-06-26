import numpy as np
import pandas as pd

import config
from finansal.utils import safe_set


def test_safe_set_casts_to_config_dtype():
    df = pd.DataFrame({"adx_14": pd.Series([1, 2], dtype="int64")})
    safe_set(df, "adx_14", np.array([1.5, 2.5]))
    assert df["adx_14"].dtype == config.DTYPES_MAP["adx_14"]
