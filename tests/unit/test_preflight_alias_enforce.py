from pathlib import Path

import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    df = pd.DataFrame({"close": [1]})
    excel_dir = tmp_path / "excels"
    excel_dir.mkdir()
    df.to_excel(excel_dir / "sample.xlsx", index=False)
    filters_path = tmp_path / "filters.csv"
    content = "FilterCode;PythonQuery\nF1;SMA50 > 0\n"
    filters_path.write_text(content, encoding="utf-8")
    return filters_path, excel_dir


def test_alias_forbid(tmp_path: Path) -> None:
    filters_path, excel_dir = _setup(tmp_path)
    with pytest.raises(SystemExit):
        validate_filters(filters_path, excel_dir, alias_mode="forbid")


def test_alias_warn(tmp_path: Path) -> None:
    filters_path, excel_dir = _setup(tmp_path)
    with pytest.warns(UserWarning):
        validate_filters(filters_path, excel_dir, alias_mode="warn")
