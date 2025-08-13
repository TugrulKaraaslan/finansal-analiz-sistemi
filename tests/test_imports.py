def test_imports():
    import numpy as np
    import pandas as pd

    import backtest
    from backtest import data_loader, indicators, screener

    assert np and pd and backtest and indicators and screener and data_loader
