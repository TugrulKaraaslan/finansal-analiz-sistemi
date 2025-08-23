from hypothesis import given, strategies as st
from backtest.eval.walk_forward import WfParams, generate_folds


@given(
    train=st.integers(min_value=1, max_value=10),
    test=st.integers(min_value=1, max_value=5),
    step=st.integers(min_value=1, max_value=5),
)
def test_no_leakage(train, test, step):
    p = WfParams(
        "2025-03-01",
        "2025-03-20",
        train_days=train,
        test_days=test,
        step_days=step,
    )
    folds = generate_folds(p)
    for f in folds:
        assert f["train_end"] < f["test_start"]
