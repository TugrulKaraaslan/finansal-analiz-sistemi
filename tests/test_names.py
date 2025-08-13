from backtest.utils.names import canonical_name


def test_alias_cases():
    pairs = {
        "EMA20": "ema_20",
        "EMA_20": "ema_20",
        "ema20": "ema_20",
        "ema_20": "ema_20",
        "SMA200": "sma_200",
        "sma-50": "sma_50",
        "rsi14": "rsi_14",
        "ADX14": "adx_14",
        "stochrsik_14_14_3_3": "stochrsi_k",
        "STOCHRSId_14_14_3_3": "stochrsi_d",
        "williams%r14": "williams_percent_r_14",
    }
    for raw, want in pairs.items():
        assert canonical_name(raw) == want


def test_imports():
    import backtest
    from backtest.utils import names

    assert backtest and names
