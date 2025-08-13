def test_imports():
    import numpy as np  # noqa: F401
    import pandas as pd  # noqa: F401
    try:
        import pandas_ta  # noqa: F401
    except ModuleNotFoundError:
        pass
    import backtest  # noqa: F401
    from backtest import indicators, screener, data_loader  # noqa: F401
