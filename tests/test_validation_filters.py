import pandas as pd
from pathlib import Path
import tempfile
from backtest.validation import validate_filters

CSV_CONTENT = """FilterCode,PythonQuery
F1,rsi_14 > 50
F2,
F1,close > 10
"""


def test_validation_detects_errors():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(CSV_CONTENT)
        fname = f.name
    rep = validate_filters(fname)
    codes = [e["code"] for e in rep.errors]
    assert "VC002" in codes  # boş query
    assert "VC001" in codes  # FilterCode tekrarı
