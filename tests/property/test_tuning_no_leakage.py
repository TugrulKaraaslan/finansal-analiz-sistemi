from hypothesis import given, strategies as st
import pandas as pd

from backtest.cv.timeseries import PurgedKFold, WalkForward


given_size = st.integers(min_value=12, max_value=40)


@given(given_size)
def test_purged_kfold_leakage(n):
    data = pd.DataFrame({"returns": [0] * n})
    splitter = PurgedKFold(n_splits=3, embargo=2)
    for train_idx, test_idx in splitter.split(data):
        assert set(train_idx).isdisjoint(set(test_idx))
        embargo_zone = set(range(test_idx[0] - 2, test_idx[-1] + 3))
        assert set(train_idx).isdisjoint(embargo_zone)


@given(given_size)
def test_walk_forward_leakage(n):
    data = pd.DataFrame({"returns": [0] * n})
    splitter = WalkForward(folds=3, embargo=2)
    for train_idx, test_idx in splitter.split(data):
        assert max(train_idx) + 2 <= min(test_idx)
