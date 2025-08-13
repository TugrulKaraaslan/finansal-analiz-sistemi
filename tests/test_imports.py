def test_imports():
    import numpy as np, pandas as pd, pandas_ta as ta  # noqa
    import backtest  # noqa: F401
    from backtest import indicators, screener, data_loader  # noqa
