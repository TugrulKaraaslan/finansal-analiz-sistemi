import pandas as pd

from backtest.filters.engine import evaluate


def _df():
    s = pd.Series([0, 1, 2, 1, 2, 3])
    return pd.DataFrame(
        {
            "a": s,
            "b": s.shift(1).fillna(0),
            "macd_line": [0.1, -0.2, 0.3, -0.1, 0.2, 0.5],
        }
    )


def test_aliases_equivalent():
    df = _df()
    exprs_up = [
        "cross_up(a,b)",
        "CROSSUP(a,b)",
        "crossOver(a,b)",
        "keser_yukari(a,b)",
        "cross_over(a,b)",
    ]
    masks = [evaluate(df, e) for e in exprs_up]
    for m in masks[1:]:
        assert m.equals(masks[0])

    exprs_down = [
        "cross_down(a,b)",
        "CROSSDOWN(a,b)",
        "crossUnder(a,b)",
        "keser_asagi(a,b)",
        "cross_under(a,b)",
    ]
    masks_down = [evaluate(df, e) for e in exprs_down]
    for m in masks_down[1:]:
        assert m.equals(masks_down[0])


def test_constant_level_aliases():
    df = _df()
    exprs = [
        "cross_up(macd_line, 0.0)",
        "CROSSUP(macd_line, 0.0)",
    ]
    masks = [evaluate(df, e) for e in exprs]
    for m in masks[1:]:
        assert m.equals(masks[0])


def test_na_policy():
    df = _df()
    mask_up = evaluate(df, "cross_up(a,b)")
    assert list(mask_up) == [False, True, False, False, True, False]
    mask_down = evaluate(df, "cross_down(a,b)")
    assert list(mask_down) == [False, False, False, True, False, False]


def test_cross_over_alias():
    df = _df()
    m1 = evaluate(df, "cross_up(a,b)")
    m2 = evaluate(df, "cross_over(a,b)")
    assert m1.equals(m2)
