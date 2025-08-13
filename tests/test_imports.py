def test_imports():
    import numpy as np
    import pandas as pd

    # pandas_ta opsiyonel: yoksa test patlamasın
    try:
        import pandas_ta as _pta  # noqa: F401

        has_pandas_ta = True
    except ModuleNotFoundError:
        has_pandas_ta = False

    import backtest

    # Alt modüller yüklenebiliyor mu? (sıra önemli değil)
    from backtest import data_loader, indicators, screener  # noqa: F401

    # Temel varlık kontrolleri
    assert np is not None and pd is not None and backtest is not None
    assert data_loader is not None and indicators is not None and screener is not None

    # pandas_ta varsa import edilip edilmediğini de doğrula
    if has_pandas_ta:
        assert "_pta" in locals()
