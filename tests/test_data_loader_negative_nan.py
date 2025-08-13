import pandas as pd

from backtest.data_loader import read_excels_long


def test_read_excels_long_negative_and_nan(tmp_path):
    f = tmp_path / "dummy.xlsx"
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "open": [1, None, 3],
            "high": [2, 3, -4],
            "low": [1, 2, 3],
            "close": [1, 2, 3],
            "volume": [100, 200, 300],
        }
    )
    df.to_excel(f, index=False)

    out = read_excels_long(tmp_path)
    assert len(out) == 1

    df.loc[2, "high"] = 4
    df.to_excel(f, index=False)

    out = read_excels_long(tmp_path)
    assert len(out) == 2
    assert out[["open", "high", "low", "close", "volume"]].isna().sum().sum() == 0
    assert not (out[["open", "high", "low", "close", "volume"]] < 0).any().any()
