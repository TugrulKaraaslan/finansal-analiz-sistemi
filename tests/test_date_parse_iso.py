import os
import sys
import types
import importlib
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_parse_date_iso(monkeypatch):
    for m in [
        "data_loader",
        "preprocessor",
        "indicator_calculator",
        "filter_engine",
        "backtest_core",
        "report_generator",
    ]:
        monkeypatch.setitem(sys.modules, m, types.ModuleType(m))

    import main
    importlib.reload(main)

    assert main._parse_date("2025-03-07") == pd.Timestamp("2025-03-07")
    assert main._parse_date("07.03.2025") == pd.Timestamp("2025-03-07")
