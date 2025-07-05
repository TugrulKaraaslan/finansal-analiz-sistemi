import pandas as pd

import portfolio_builder
from finansal_analiz_sistemi import config


def test_calculate_total_return_weight(monkeypatch):
    df = pd.DataFrame({"raw_return": [0.1, 0.2]})
    monkeypatch.setattr(config, "filter_weights", {"F1": 0.5})
    result = portfolio_builder.calculate_total_return("F1", df)
    assert result == 0.15000000000000002


def test_calculate_total_return_missing(monkeypatch):
    df = pd.DataFrame({"other": [1, 2]})
    monkeypatch.setattr(config, "filter_weights", {})
    assert portfolio_builder.calculate_total_return("X", df) == 0.0
