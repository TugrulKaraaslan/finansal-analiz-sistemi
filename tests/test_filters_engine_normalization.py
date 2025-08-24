import pandas as pd

from backtest.batch import run_scan_day
from backtest.filters.engine import evaluate
from backtest.screener import run_screener


def _simple_df():
    s = pd.Series([0, 1, 2, 1, 2, 3])
    return pd.DataFrame({"a": s, "b": s.shift(1).fillna(0)})


def test_cross_variants_same_mask():
    df = _simple_df()
    exprs_up = [
        "cross_up(a,b)",
        "CROSSUP(a,b)",
        "crossOver(a,b)",
        "keser_yukari(a,b)",
    ]
    masks = [evaluate(df, e) for e in exprs_up]
    for m in masks[1:]:
        assert m.equals(masks[0])

    exprs_down = [
        "cross_down(a,b)",
        "CROSSDOWN(a,b)",
        "crossUnder(a,b)",
        "keser_asagi(a,b)",
    ]
    masks_down = [evaluate(df, e) for e in exprs_down]
    for m in masks_down[1:]:
        assert m.equals(masks_down[0])


def test_screener_batch_consistency():
    idx = pd.date_range("2024-01-01", periods=1, freq="B")
    df_batch = pd.DataFrame(
        {
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [2],
            "volume": [1],
        },
        index=idx,
    )
    filters_df = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > open"]})
    rows_batch = run_scan_day(df_batch, str(idx[0].date()), filters_df)

    df_screen = df_batch.reset_index().rename(columns={"index": "date"})
    df_screen["symbol"] = "SYM"
    rows_screen = run_screener(df_screen, filters_df, idx[0])

    assert len(rows_batch) == len(rows_screen) == 1
