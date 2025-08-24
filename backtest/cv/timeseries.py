from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Tuple

import numpy as np
import pandas as pd

from backtest.strategy import StrategySpec, run_strategy, score


@dataclass
class PurgedKFold:
    n_splits: int
    embargo: int = 0

    def split(self, data: pd.DataFrame) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        n = len(data)
        fold_size = n // self.n_splits
        for i in range(self.n_splits):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size
            train_left_end = max(0, test_start - self.embargo)
            train_right_start = min(n, test_end + self.embargo)
            train_idx = np.concatenate(
                [np.arange(0, train_left_end), np.arange(train_right_start, n)]
            )
            test_idx = np.arange(test_start, test_end)
            yield train_idx, test_idx


@dataclass
class WalkForward:
    folds: int
    embargo: int = 0

    def split(self, data: pd.DataFrame) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        n = len(data)
        fold_size = n // (self.folds + 1)
        for i in range(self.folds):
            train_end = fold_size * (i + 1)
            test_start = train_end + self.embargo
            test_end = test_start + fold_size
            if test_end > n:
                break
            train_idx = np.arange(0, train_end)
            test_idx = np.arange(test_start, test_end)
            yield train_idx, test_idx


def cross_validate(
    spec: StrategySpec,
    data: pd.DataFrame,
    splitter: PurgedKFold | WalkForward,
    constraints: dict,
) -> List[float]:
    """Run cross-validation and return list of fold scores."""

    scores: List[float] = []
    for _, test_idx in splitter.split(data):
        test_data = data.iloc[test_idx]
        res = run_strategy(spec, test_data, exec_cfg=None)
        scores.append(score(res, constraints))
    return scores
