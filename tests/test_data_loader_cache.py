import time
from types import SimpleNamespace

import pandas as pd

from backtest.data_loader import read_excels_long


def _make_excels(tmp_path, count):
    for i in range(count):
        df = pd.DataFrame({"date": ["2020-01-01"], "close": [i]})
        df.to_excel(tmp_path / f"f{i}.xlsx", index=False)


def test_read_excels_long_cache_speed(tmp_path):
    _make_excels(tmp_path, 6)
    cfg = SimpleNamespace(
        data=SimpleNamespace(
            excel_dir=tmp_path, enable_cache=None, cache_parquet_path=tmp_path / "cache.parquet"
        )
    )
    start = time.perf_counter()
    read_excels_long(cfg)
    first = time.perf_counter() - start
    start = time.perf_counter()
    read_excels_long(cfg)
    second = time.perf_counter() - start
    assert second <= first
