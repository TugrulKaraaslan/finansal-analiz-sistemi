import numpy as np
import pandas as pd
import pytest

from backtest.guardrails.no_lookahead import check_warmup


def test_check_warmup_enforces_nan_before_window():
    df = pd.DataFrame({'signal': [np.nan, np.nan, 1.0, 0.0]})
    check_warmup(df[['signal']], 2)  # ok
    df_bad = pd.DataFrame({'signal': [1.0, np.nan, 0.5]})
    with pytest.raises(AssertionError):
        check_warmup(df_bad[['signal']], 2)
