import pandas as pd

from backtest.downloader.schema import CANON_COLS, normalize


def test_normalize_decimal_and_sort():
    df = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-01", "2024-01-01"],
            "open": ["1,5", "2,0", "2,0"],
            "high": ["2,5", "3,0", "3,0"],
            "low": ["1,0", "1,5", "1,5"],
            "close": ["2,0", "2,5", "2,5"],
            "volume": ["1", "2", "2"],
            "quantity": ["10", "20", "20"],
        }
    )
    norm = normalize(df)
    assert norm["date"].is_monotonic_increasing
    assert len(norm) == 2  # duplicate date dropped
    assert list(norm.columns) == CANON_COLS
    assert norm["open"].dtype == "float64"
    assert norm["volume"].dtype == "int64"
