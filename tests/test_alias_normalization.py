import pandas as pd

from backtest.filters_compile import compile_expression
from backtest.naming.aliases import normalize_token


def test_token_normalization_examples():
    cases = {
        "SMA50": "sma_50",
        "sma-50": "sma_50",
        "ADX14": "adx_14",
        "BBU_20_2.0": "bbu_20_2",
        "hacim": "volume",
        "islem_hacmi": "volume",
        "lot": "volume",
        "MACD_line": "macd_line",
        "macd-signal": "macd_signal",
        "bbm_20.5_2": "bbm_20p5_2",
    }
    for raw, expected in cases.items():
        assert normalize_token(raw) == expected


def test_compiler_normalization_equivalence():
    df = pd.DataFrame({"sma_50": [1], "close": [0]})
    fn_alias = compile_expression("SMA50 > close", normalize=True)
    fn_canon = compile_expression("sma_50 > close", normalize=True)
    assert fn_alias(df).equals(fn_canon(df))
