def test_imports():
    import numpy as np
    import pandas as pd

    try:
        import pandas_ta
        assert pandas_ta
    except ModuleNotFoundError:
        pass

    import backtest
    from backtest import indicators, screener, data_loader

    assert np and pd and backtest and indicators and screener and data_loader
