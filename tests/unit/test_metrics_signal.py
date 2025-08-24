import pandas as pd

from backtest.eval.metrics import SignalMetricConfig, signal_metrics_for_filter


def test_signal_metrics_perfect():
    df = pd.DataFrame({"close": [100, 101, 102, 103, 104, 105], "sig": [0, 1, 0, 1, 0, 0]})
    cfg = SignalMetricConfig(horizon_days=1, threshold_bps=0, price_col="close")
    m = signal_metrics_for_filter(df, "sig", cfg)
    assert 0 <= m["precision"] <= 1 and 0 <= m["recall"] <= 1
