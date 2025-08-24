from backtest.naming import (
    CANONICAL_SET,
    load_alias_map,
    normalize_indicator_token,
    to_snake,
)
from backtest.paths import ALIAS_PATH

ALIAS_CSV = ALIAS_PATH


def test_to_snake_basic():
    assert to_snake("Adj Close") == "adj_close"
    assert to_snake("RSI_14") == "rsi_14"
    assert to_snake("Ağırlıklı Ortalama") == "a_girlikli_ortalama"  # dil sapması normalize edilir


def test_alias_load_and_resolve():
    amap = load_alias_map(ALIAS_CSV)
    # örnek aliaslar csv'de var
    assert amap.resolve("EMA50") == "ema_50"
    assert amap.resolve("MACD_HIST") == "macd_hist_12_26_9"


def test_normalize_indicator_token_with_alias():
    amap = load_alias_map(ALIAS_CSV)
    norm = normalize_indicator_token("RSI14", amap.mapping)
    assert norm == "rsi_14"


def test_canonical_presence():
    # kritik kanonikler mevcut mu?
    required = {
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap_d",
        "rsi_14",
        "ema_50",
        "bbl_20_2",
        "bbh_20_2",
        "macd_12_26_9",
        "macd_signal_12_26_9",
        "macd_hist_12_26_9",
        "adx_14",
        "dmp_14",
        "dmn_14",
        "aroon_up_14",
        "aroon_down_14",
    }
    assert required.issubset(CANONICAL_SET)
