from backtest.eval.walk_forward import WfParams, generate_folds


def test_basic_splits():
    p = WfParams(
        "2025-03-07",
        "2025-03-11",
        train_days=2,
        test_days=1,
        step_days=1,
    )
    folds = generate_folds(p)
    assert folds, "no folds generated"
    # Sıralı ve sızma yok
    for f in folds:
        assert f["train_start"] <= f["train_end"]
        assert f["train_end"] < f["test_start"]
        assert f["test_start"] <= f["test_end"]

    # step_days=1 ise test başlangıçları ardışık
    starts = [f["test_start"] for f in folds]
    assert sorted(starts) == starts
