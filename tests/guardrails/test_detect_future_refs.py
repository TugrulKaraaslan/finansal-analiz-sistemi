import pytest

from backtest.guardrails.no_lookahead import detect_future_refs


@pytest.mark.parametrize("expr", ["shift(-1)", "lead(close,1)", "next_close", "t+1"])
def test_detect_future_refs(expr):
    with pytest.raises(AssertionError):
        detect_future_refs(expr)


def test_allow_past_reference():
    detect_future_refs("close.shift(1)")
