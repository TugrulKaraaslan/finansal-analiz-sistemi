import pandas as pd
import numpy as np
from backtest.dsl import Evaluator, SeriesContext, parse_expression

idx = pd.date_range("2024-01-01", periods=5, freq="B")


def _ctx(**series):
    vals = {}
    for k, v in series.items():
        if isinstance(v, (list, tuple, np.ndarray)):
            vals[k] = pd.Series(v, index=idx)
        else:
            vals[k] = v
    return SeriesContext(vals)


def test_simple_compare_and_logic():
    ctx = _ctx(
        rsi_14=[50, 56, 60, np.nan, 40],
        ema_50=[10, 10, 10, 10, 10],
        close=[11, 9, 11, 12, 8],
    )
    ev = Evaluator(ctx)
    out = ev.eval("rsi_14 > 55 and close > ema_50")
    # Beklenen: [False, True, True, False, False]
    assert out.tolist() == [False, True, True, False, False]


def test_cross_up_and_down():
    a = [9, 10, 11, 10, 12]
    b = [10, 10, 10, 10, 10]
    ctx = _ctx(a=a, b=b)
    ev = Evaluator(ctx)
    up = ev.eval("cross_up(a,b)")
    dn = ev.eval("cross_down(a,b)")
    assert up.tolist() == [
        False,
        False,
        True,
        False,
        False,
    ]  # 10→11, 10 çizgisi yukarı kesildi
    assert dn.tolist() == [False, False, False, True, False]  # 11→10, aşağı kesildi


def test_forbidden_ast():
    # lambda, listcomp vb. yasak
    try:
        parse_expression("(lambda x: x)(1)")
        assert False, "yasak düğüm kaçtı"
    except Exception as e:
        assert hasattr(e, "code") and e.code == "DF002"


def test_unknown_name_and_func():
    ctx = _ctx(close=[1, 2, 3, 4, 5])
    ev = Evaluator(ctx)
    try:
        ev.eval("unknown_series > 5")
        assert False, "tanımsız seri kaçtı"
    except Exception as e:
        assert getattr(e, "code", None) == "DF003"
    try:
        ev.eval("unknown_func(close)")
        assert False, "tanımsız fonksiyon kaçtı"
    except Exception as e:
        assert getattr(e, "code", None) == "DF003"


def test_nan_policy():
    ctx = _ctx(x=[1, np.nan, 3, 4, 5], y=[0, 0, 0, 0, 0])
    ev = Evaluator(ctx)
    out = ev.eval("x > y")
    assert out.tolist() == [True, False, True, True, True]
