from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("pyarrow")

from finansal.parquet_cache import ParquetCacheManager


def test_refresh_and_load(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    cache_path = tmp_path / "cache.parquet"

    # prepare sample csv
    df_in = pd.DataFrame({"x": [1, 2, 3]})
    df_in.to_csv(csv_path, index=False)

    mngr = ParquetCacheManager(cache_path)
    df_cached = mngr.refresh(csv_path)
    assert len(df_cached) == 3

    df_loaded = mngr.load()
    pd.testing.assert_frame_equal(df_cached, df_loaded)


def test_load_missing(tmp_path: Path) -> None:  # noqa: D401
    mngr = ParquetCacheManager(tmp_path / "missing.parquet")
    with pytest.raises(FileNotFoundError):
        _ = mngr.load()
