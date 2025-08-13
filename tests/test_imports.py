def test_imports():
    import numpy as np
    import pandas as pd
    try:
        import pandas_ta
    except ModuleNotFoundError:
        pandas_ta = None
    import backtest
    from backtest import indicators, screener, data_loader
    assert np and pd and backtest and indicators and screener and data_loader
    if pandas_ta:
        assert pandas_ta
