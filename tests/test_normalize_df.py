import pandas as pd

from backtest.normalize import CollisionError, normalize_dataframe
from backtest.paths import ALIAS_PATH

ALIAS = str(ALIAS_PATH)


def _df():
    return pd.DataFrame(
        {
            "Open": [1, 2],
            "Adj Close": [10, 11],
            "Close": [10, 11],
            "Close.1": [10, 11],
            "VOL": [100, 110],
            "RSI_14": [55, 45],
            "Custom Field": [0, 1],
        }
    )


def test_strict_collision_raises():
    df = _df()
    try:
        _ = normalize_dataframe(df, ALIAS, policy="strict")
        assert False, "strict modda çakışma yakalanmalıydı"
    except CollisionError as e:
        assert e.code == "VN001"


def test_prefer_first_drops_duplicates():
    df = _df()
    out, rep = normalize_dataframe(df, ALIAS, policy="prefer_first")
    assert "Close.1" in rep.dropped
    assert "open" in out.columns and "volume" in out.columns
    assert "close" in out.columns


def test_suffix_policy_renames_duplicates():
    df = _df()
    out, rep = normalize_dataframe(df, ALIAS, policy="suffix")
    # close, close_dup1, close_dup2 gibi
    assert any(c.startswith("close_dup") for c in out.columns)


def test_alias_and_snake_case_applied():
    df = _df()
    out, rep = normalize_dataframe(df, ALIAS, policy="prefer_first")
    assert "open" in out.columns
    assert "volume" in out.columns  # VOL -> volume
    assert "rsi_14" in out.columns  # RSI_14 -> rsi_14
    # Custom Field -> custom_field (alias yoksa yalnız snake)
    assert "custom_field" in out.columns
