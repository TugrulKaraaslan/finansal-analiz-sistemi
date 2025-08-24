from pathlib import Path

import pandas as pd

from backtest.filters.preflight import validate_filters


def test_preflight_ok(tmp_path):
    df = pd.DataFrame({"close": [1], "volume": [2]})
    excel_dir = tmp_path / "excels"
    excel_dir.mkdir()
    df.to_excel(excel_dir / "sample.xlsx", index=False)
    filters = Path("tests/data/filters_valid.csv")
    validate_filters(filters, excel_dir)
