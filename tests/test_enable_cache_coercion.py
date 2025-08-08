import pandas as pd
import pytest

from backtest.data_loader import read_excels_long


@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        (1, True),
        (True, True),
        ("false", False),
        (0, False),
        (False, False),
    ],
)
def test_enable_cache_coercion(tmp_path, monkeypatch, value, expected):
    df = pd.DataFrame({"a": [1]})
    cache_file = tmp_path / "cache.parquet"
    cache_file.write_text("dummy")
    monkeypatch.setattr(pd, "read_parquet", lambda _: df)

    config = {
        "data": {
            "excel_dir": tmp_path,
            "enable_cache": value,
            "cache_parquet_path": cache_file,
        }
    }

    if expected:
        result = read_excels_long(config)
        assert result.equals(df)
    else:
        with pytest.raises(RuntimeError):
            read_excels_long(config)
