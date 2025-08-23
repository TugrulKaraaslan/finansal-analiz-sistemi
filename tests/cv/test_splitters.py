import pandas as pd

from backtest.cv.timeseries import PurgedKFold, WalkForward


def test_purged_kfold_no_overlap():
    data = pd.DataFrame({"returns": [0] * 10})
    splitter = PurgedKFold(n_splits=2, embargo=1)
    for train_idx, test_idx in splitter.split(data):
        assert set(train_idx).isdisjoint(set(test_idx))
        span = set(range(test_idx[0] - 1, test_idx[-1] + 2))
        assert set(train_idx).isdisjoint(span)


def test_walk_forward_no_overlap():
    data = pd.DataFrame({"returns": [0] * 15})
    splitter = WalkForward(folds=3, embargo=1)
    for train_idx, test_idx in splitter.split(data):
        assert max(train_idx) < min(test_idx)
        assert min(test_idx) - max(train_idx) > 1
