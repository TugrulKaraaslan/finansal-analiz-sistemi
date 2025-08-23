import pandas as pd
from backtest.eval.metrics import equity_metrics

def test_equity_mdd_and_mar():
    eq = pd.DataFrame({'date': pd.date_range('2025-01-01', periods=5, freq='D'), 'equity':[100,110,120,90,95]})
    em = equity_metrics(eq)
    assert em['max_drawdown'] <= 0
    assert 'mar' in em
