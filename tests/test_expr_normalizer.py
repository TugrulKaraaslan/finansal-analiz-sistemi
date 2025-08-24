from backtest.filters.normalize_expr import normalize_expr


def test_decimal_fragment_removed():
    expr = "cci_20_0 .015 > 100"
    assert normalize_expr(expr)[0] == "cci_20 > 100"


def test_logical_ops_and_or():
    expr = "a and b or c"
    assert normalize_expr(expr)[0] == "a & b | c"


def test_stochrsi_typos():
    expr = "stochrsik_14_14_3_3 > 0.8"
    assert normalize_expr(expr)[0] == "stochrsi_k_14_14_3_3 > 0.8"


def test_string_literals_preserved():
    expr = 'col == "a and b" or flag'
    assert normalize_expr(expr)[0] == 'col == "a and b" | flag'


def test_psarl_dotted_to_underscored():
    s, _ = normalize_expr("psarl_0.02_0.2 < close")
    assert s == "psarl_0_02_0_2 < close"


def test_willr_negative_levels():
    s, _ = normalize_expr("willr_14 > _100 and crossup(willr_14, _80)")
    assert s == "willr_14 > -100 & cross_up(willr_14,-80)"


def test_space_eq_fixed():
    s, _ = normalize_expr("aroon_up_14 = = 100")
    assert s == "aroon_up_14 == 100"
