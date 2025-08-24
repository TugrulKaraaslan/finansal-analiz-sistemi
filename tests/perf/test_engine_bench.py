import pandas as pd
import numpy as np
import pytest
from backtest.filters.engine import evaluate

pytestmark = pytest.mark.perf
pytest.importorskip("pytest_benchmark")

@pytest.fixture
def df():
    n = 50_000
    return pd.DataFrame({
        'ichimoku_conversionline': np.random.rand(n)*100,
        'ichimoku_baseline': np.random.rand(n)*100,
        'macd_line': np.random.randn(n)/10,
        'macd_signal': np.random.randn(n)/10,
        'bbm_20_2': np.random.rand(n)*100,
        'bbu_20_2': np.random.rand(n)*100+1,
        'bbl_20_2': np.random.rand(n)*100-1,
    })

@pytest.mark.benchmark(group="evaluate")
def test_evaluate_macd_vs_signal(benchmark, df):
    benchmark(lambda: evaluate(df, 'macd_line > macd_signal'))

@pytest.mark.benchmark(group="evaluate")
def test_evaluate_bbands_cross(benchmark, df):
    benchmark(lambda: evaluate(df, 'cross_up(bbm_20_2, bbl_20_2)'))
