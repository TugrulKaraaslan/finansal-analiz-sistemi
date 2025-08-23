import pandas as pd
from backtest.filters.preflight import validate_filters


def test_alias_allowed(tmp_path):
    excel_dir = tmp_path / "excels"
    excel_dir.mkdir()
    df = pd.DataFrame({"close": [1]})
    df.to_excel(excel_dir / "sample.xlsx", index=False)
    f = tmp_path / "filters.csv"
    f.write_text(
        "FilterCode,PythonQuery\nX1,its_9 > iks_26\n",
        encoding="utf-8",
    )
    validate_filters(f, excel_dir, alias_mode="allow", allow_unknown=True)
