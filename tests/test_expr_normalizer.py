from backtest.filters.normalize_expr import normalize_expr


def test_decimal_fragment_removed():
    expr = "cci_20_0 .015 > 100"
    assert normalize_expr(expr) == "cci_20_0 > 100"


def test_logical_ops_and_or():
    expr = "a and b or c"
    assert normalize_expr(expr) == "a & b | c"


def test_stochrsi_typos():
    expr = "stochrsik_14_14_3_3 > 0.8"
    assert normalize_expr(expr) == "stochrsi_k_14_14_3_3 > 0.8"


def test_string_literals_preserved():
    expr = 'col == "a and b" or flag'
    assert normalize_expr(expr) == 'col == "a and b" | flag'
