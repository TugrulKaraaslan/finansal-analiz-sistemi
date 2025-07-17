import pandas as pd

from data_loader_cache import DataLoaderCache
from src.utils.excel_reader import open_excel_cached


def test_clear_also_empties_excel_cache(tmp_path):
    path = tmp_path / "a.xlsx"
    pd.DataFrame({"x": [1]}).to_excel(path, index=False)

    cache = DataLoaderCache()
    first = cache.load_excel(str(path))
    # ensure the workbook comes from the cache
    second = open_excel_cached(path)
    assert first is second

    cache.clear()
    new = cache.load_excel(str(path))
    assert new is not first
