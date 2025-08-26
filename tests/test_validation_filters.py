from io import StringIO

import pandas as pd

from backtest.validation import validate_filters

CSV_CONTENT = """FilterCode;PythonQuery
F1;rsi_14 > 50
F2;
F1;close > 10
"""


def test_validation_detects_errors():
    df = pd.read_csv(StringIO(CSV_CONTENT), sep=";")
    rep = validate_filters(df)
    codes = [e["code"] for e in rep.errors]
    assert "VC002" in codes  # boş query
    assert "VC001" in codes  # FilterCode tekrarı
