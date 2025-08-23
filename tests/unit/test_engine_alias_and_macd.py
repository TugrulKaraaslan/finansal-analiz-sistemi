import pandas as pd
from backtest.filters.engine import evaluate

def _df():
    return pd.DataFrame({
        'ichimoku_conversionline': [1, 2, 3],
        'ichimoku_baseline': [1, 1, 4],
        'macd_line': [0.1, -0.2, 0.3],
        'macd_signal': [0.0, 0.0, 0.0],
    })

def test_alias_ichimoku():
    s = evaluate(_df(), 'its_9 > iks_26')
    assert s.dtype == 'bool' and len(s) == 3

def test_macd_names():
    s = evaluate(_df(), 'macd_line > macd_signal')
    assert s.tolist() == [True, False, True]
