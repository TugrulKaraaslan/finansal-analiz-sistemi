# indicator_calculator.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Teknik İndikatörler ve Kesişim Sinyalleri Hesaplama
# Tuğrul Karaaslan & Gemini

from __future__ import annotations

import gc
import re
import warnings

# Ensure pandas_ta can locate its distribution info. Some environments lazily
# query ``importlib.metadata`` so simply importing the module can help locate
# the package metadata. Assign the module to a dummy variable to silence
# linters complaining about an unused import.
from importlib import metadata as _metadata
from pathlib import Path

import numpy as np
import pandas as pd
import pandas.errors

import utils
from config_loader import load_ema_close_crossovers
from finansal.utils import lazy_chunk, safe_set
from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.config import CHUNK_SIZE
from finansal_analiz_sistemi.log_tools import PCT_STEP
from finansal_analiz_sistemi.utils.normalize import normalize_filtre_kodu
from logging_config import get_logger
from openbb_missing import ichimoku as obb_ichimoku
from openbb_missing import macd as obb_macd
from openbb_missing import rsi as obb_rsi
from utilities.naming import unique_name
from utils.compat import safe_concat

_unused_metadata = _metadata

# Tarih: 19 Mayıs 2025 (Tüm özel fonksiyonlar eklendi, reset_index
# düzeltildi, filtre uyumu artırıldı v2)


# numpy>=2.0 paketlerinde `NaN` sabiti kaldırıldı. pandas_ta halen bu adı
# kullandığından import sırasında hata oluşabiliyor. Eğer `np.NaN` mevcut
# değilse `np.nan` değerini aynı isimle tanımlayarak uyumluluk sağlanır.
if not hasattr(np, "NaN"):
    np.NaN = np.nan


try:
    import pandas_ta as ta
except ImportError as exc:  # pragma: no cover - dependency missing
    raise RuntimeError(
        "pandas-ta-openbb not installed. Run: pip install pandas-ta-openbb"
    ) from exc

try:  # pragma: no cover - optional indicator
    from pandas_ta import psar as ta_psar
except Exception:  # pragma: no cover - missing indicator
    ta_psar = None  # type: ignore[misc]

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
warnings.filterwarnings(
    "ignore",
    message="A value is trying to be set on a copy of a DataFrame or Series",
    category=FutureWarning,
    module="indicator_calculator",
)
warnings.filterwarnings(
    "ignore",
    message="Series.fillna with 'method' is deprecated",
    category=FutureWarning,
    module="indicator_calculator",
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Otomatik EMA/kapanış kesişim sütunları
# ---------------------------------------------------------------------------
EMA_CLOSE_PATTERN = re.compile(r"ema_(\d+)_keser_close_(yukari|asagi)")


def _calc_ema(df: pd.DataFrame, n: int) -> pd.Series:
    if "close" not in df.columns:
        return pd.Series(np.nan, index=df.index)
    return df["close"].ewm(span=n, adjust=False).mean()


def add_crossovers(df: pd.DataFrame, cross_names: list[str]) -> pd.DataFrame:
    """Generate crossover columns based on naming patterns."""
    for name in cross_names:
        m = EMA_CLOSE_PATTERN.fullmatch(name)
        if m:
            span = int(m.group(1))
            direction = m.group(2)
            ema = _calc_ema(df, span)
            if direction == "yukari":
                cross = utils.crosses_above(ema, df["close"]).astype(int)
            else:
                cross = utils.crosses_below(ema, df["close"]).astype(int)
            df[name] = cross
            continue
        raise ValueError(f"Bilinmeyen crossover format\u0131: {name}")
    return df


def _calculate_combined_psar(group_df: pd.DataFrame) -> pd.Series:
    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    sutun_adi = "psar"
    try:
        if "psar" in group_df.columns:
            psar_col = group_df["psar"]
            if isinstance(psar_col, pd.DataFrame):
                psar_col = psar_col.iloc[:, 0]
            return psar_col.rename(sutun_adi)
        if "psar_long" in group_df.columns and "psar_short" in group_df.columns:
            combined_psar = group_df["psar_long"].fillna(group_df["psar_short"])
            return combined_psar.rename(sutun_adi)
        else:
            logger.debug(
                f"{hisse_str}: Birleşik PSAR için 'psar_long' veya 'psar_short' sütunları bulunamadı."
            )
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
    except Exception as e:
        logger.error(
            f"{hisse_str}: Birleşik PSAR hesaplanırken hata: {e}", exc_info=False
        )
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def _calculate_relative_volume(
    group_df: pd.DataFrame, window: int, col_name_prefix: str = "volume"
) -> pd.Series:
    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    sutun_adi = next(
        (
            item["name"]
            for item in config.OZEL_SUTUN_PARAMS
            if item["function"] == "_calculate_relative_volume"
        ),
        "relative_volume_default",
    )
    try:
        vol_column = col_name_prefix
        if vol_column not in group_df.columns:
            logger.debug(
                f"{hisse_str}: Relative Volume ({sutun_adi}) için '{vol_column}' sütunu bulunamadı."
            )
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        if len(group_df) < window:
            logger.debug(
                f"{hisse_str}: {sutun_adi} hesaplamak için yeterli veri yok ({len(group_df)} satır, {window} periyot gerekli)."
            )
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        avg_vol = group_df[vol_column].rolling(window=window, min_periods=window).mean()
        relative_volume_series = group_df[vol_column] / avg_vol.replace(0, np.nan)
        return relative_volume_series.rename(sutun_adi)
    except Exception as e:
        logger.error(
            f"{hisse_str}: Relative Volume ({sutun_adi}, {window}) hesaplanırken hata: {e}",
            exc_info=False,
        )
        try:
            from utils.failure_tracker import log_failure

            log_failure("indicators", sutun_adi, str(e))
        except Exception:
            pass
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def _calculate_volume_price(
    group_df: pd.DataFrame,
    col_name_prefix_vol: str = "volume",
    col_name_prefix_price: str = "close",
) -> pd.Series:
    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    sutun_adi = next(
        (
            item["name"]
            for item in config.OZEL_SUTUN_PARAMS
            if item["function"] == "_calculate_volume_price"
        ),
        "volume_price_default",
    )
    try:
        if (
            col_name_prefix_vol not in group_df.columns
            or col_name_prefix_price not in group_df.columns
        ):
            logger.debug(
                f"{hisse_str}: Hacim*Fiyat ({sutun_adi}) için '{col_name_prefix_vol}' veya '{col_name_prefix_price}' sütunu eksik."
            )
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        return (group_df[col_name_prefix_vol] * group_df[col_name_prefix_price]).rename(
            sutun_adi
        )
    except Exception as e:
        logger.error(
            f"{hisse_str}: Hacim*Fiyat ({sutun_adi}) hesaplanırken hata: {e}",
            exc_info=False,
        )
        try:
            from utils.failure_tracker import log_failure

            log_failure("indicators", sutun_adi, str(e))
        except Exception:
            pass
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def safe_ma(df: pd.DataFrame, n: int, kind: str = "sma", logger_param=None) -> None:
    """Eksikse basit veya üssel hareketli ortalama kolonu ekler."""
    if logger_param is None:
        logger_param = logger
    local_logger = logger_param
    col = f"{kind}_{n}"
    if col in df.columns and df[col].notna().all() or "close" not in df.columns:
        return
    try:
        if kind == "sma":
            safe_set(
                df,
                col,
                df["close"].rolling(window=n, min_periods=1).mean().values,
            )
        else:
            safe_set(
                df,
                col,
                df["close"].ewm(span=n, adjust=False, min_periods=1).mean().values,
            )
        df[col] = df[col].bfill()
        local_logger.debug(f"'{col}' sütunu safe_ma ile eklendi.")
    except Exception as e:
        local_logger.error(f"'{col}' hesaplanırken hata: {e}", exc_info=False)
        try:
            from utils.failure_tracker import log_failure

            log_failure("indicators", col, str(e))
        except Exception:
            pass


def safe_get(df: pd.DataFrame, col: str) -> pd.Series | None:
    """DataFrame'den güvenli sütun erişimi yapar."""
    if col not in df.columns:
        logger.debug(f"{col} eksik – crossover atlandı")
        return None
    return df[col]


def add_series(
    df: pd.DataFrame, name: str, values, seen_names: set[str] | None = None
) -> None:
    """Add a column ensuring the name is unique."""
    if seen_names is None:
        seen_names = set(df.columns)
    safe = unique_name(name, seen_names)
    safe_set(df, safe, values)


def calculate_indicators(
    df: pd.DataFrame, indicators: list[str] | None = None
) -> pd.DataFrame:
    """Calculate simple indicators like EMA/SMA for given list.

    Duplicate column names are skipped with a warning.
    """
    if indicators is None:
        return df

    out = df.copy()
    seen_names = set(out.columns)
    for ind in indicators:
        alias = ind
        try:
            if alias.startswith("ema_"):
                span = int(alias.split("_", 1)[1])
                if "close" in out.columns:
                    calc_values = out["close"].ewm(span=span, adjust=False).mean()
                else:
                    calc_values = np.nan
            elif alias.startswith("sma_"):
                span = int(alias.split("_", 1)[1])
                if "close" in out.columns:
                    calc_values = (
                        out["close"].rolling(window=span, min_periods=1).mean()
                    )
                else:
                    calc_values = np.nan
            else:
                logger.warning(f"Indicator not implemented: {alias}")
                calc_values = np.nan
        except Exception as e:
            logger.error(f"{alias} hesaplanirken hata: {e}")
            try:
                from utils.failure_tracker import log_failure

                log_failure("indicators", alias, str(e))
            except Exception:
                pass
            calc_values = np.nan
        add_series(out, alias, calc_values, seen_names)

    out = out.loc[:, ~out.columns.duplicated()]
    return out


def apply_indicators(df: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    """Small wrapper to apply ``calculate_indicators``."""
    return calculate_indicators(df, indicators)


def calculate_chunked(
    df: pd.DataFrame, active_inds: list[str], chunk_size: int = CHUNK_SIZE
) -> None:
    """Process DataFrame per ticker and append to Parquet."""
    pq_path = Path("veri/gosterge.parquet")
    for kods in lazy_chunk(df.groupby("ticker", sort=False), chunk_size):
        for _, group in kods:
            mini = group.sort_values("date").copy()
            mini = apply_indicators(mini, active_inds)
            try:
                mini.to_parquet(pq_path, partition_cols=["ticker"], append=True)
            except TypeError:
                mini.to_parquet(pq_path, partition_cols=["ticker"])
            del mini
        gc.collect()


def _tema20(series: pd.Series) -> pd.Series:
    """TEMA 20 – pandas_ta fallback."""
    if hasattr(ta, "tema"):
        try:
            return ta.tema(series, length=20)
        except Exception:  # pragma: no cover - manual fallback
            pass
    ema1 = series.ewm(span=20, adjust=False).mean()
    ema2 = ema1.ewm(span=20, adjust=False).mean()
    ema3 = ema2.ewm(span=20, adjust=False).mean()
    return (3 * ema1) - (3 * ema2) + ema3


def _ekle_psar(df: pd.DataFrame) -> None:
    """PSAR kolonlarını hesaplar ve ekler."""
    gerekli = ["high", "low", "close"]
    if any(c not in df.columns for c in gerekli):
        logger.debug("PSAR hesaplamak için gerekli sütunlar eksik")
        return
    if ta_psar is None:
        logger.debug("pandas_ta.psar bulunamadı, PSAR hesaplanamadı")
        return
    try:
        psar_raw = ta_psar(high=df["high"], low=df["low"], close=df["close"])
        if isinstance(psar_raw, pd.DataFrame):
            psar_df = psar_raw.iloc[:, :2].copy()
            psar_df.columns = ["psar_long", "psar_short"]
        else:
            psar_long, psar_short = psar_raw
            psar_df = safe_concat([psar_long, psar_short], axis=1)
            psar_df.columns = ["psar_long", "psar_short"]
        safe_set(df, "psar_long", psar_df["psar_long"].values)
        safe_set(df, "psar_short", psar_df["psar_short"].values)
        safe_set(df, "psar", df["psar_long"].fillna(df["psar_short"]).values)
    except Exception as e:
        logger.error(f"PSAR hesaplanırken hata: {e}")
        try:
            from utils.failure_tracker import log_failure

            log_failure("indicators", "psar", str(e))
        except Exception:
            pass


def _calculate_classicpivots_1h_p(group_df: pd.DataFrame) -> pd.Series:
    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    sutun_adi = "classicpivots_1h_p"
    try:
        gerekli = ["high", "low", "close"]
        if any(col not in group_df.columns for col in gerekli):
            logger.debug(f"{hisse_str}: {sutun_adi} için gerekli sütunlar eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        pivot = (group_df["high"] + group_df["low"] + group_df["close"]) / 3
        return pivot.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(
            f"{hisse_str}: {sutun_adi} hesaplanırken hata: {e}", exc_info=False
        )
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def _calculate_change_from_open(
    group_df: pd.DataFrame, col_name_open: str = "open", col_name_close: str = "close"
) -> pd.Series:
    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    sutun_adi = next(
        (
            item["name"]
            for item in config.OZEL_SUTUN_PARAMS
            if item["function"] == "_calculate_change_from_open"
        ),
        "change_from_open_percent_default",
    )
    try:
        if (
            col_name_open not in group_df.columns
            or col_name_close not in group_df.columns
        ):
            logger.debug(
                f"{hisse_str}: Açılıştan değişim ({sutun_adi}) için '{col_name_open}' veya '{col_name_close}' sütunu eksik."
            )
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        change = (
            (group_df[col_name_close] - group_df[col_name_open])
            / group_df[col_name_open].replace(0, np.nan)
            * 100
        )
        return change.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(
            f"{hisse_str}: Açılıştan değişim ({sutun_adi}) hesaplanırken hata: {e}",
            exc_info=False,
        )
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def _calculate_series_series_crossover(
    group_df: pd.DataFrame,
    s1_col: str,
    s2_col: str,
    col_name_above: str,
    col_name_below: str,
    logger_param=None,
) -> tuple[pd.Series, pd.Series] | None:
    if logger_param is None:
        logger_param = logger
    local_logger = logger_param

    if s1_col not in group_df or s2_col not in group_df:
        local_logger.debug(f"Crossover atlandı – {s1_col} / {s2_col} yok")
        return

    s1, s2 = group_df[s1_col].align(group_df[s2_col], join="inner")
    if s1.empty or not isinstance(s1, pd.Series) or not isinstance(s2, pd.Series):
        local_logger.debug(f"Crossover atlandı – {s1_col} / {s2_col} tip uygun değil")
        return

    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    empty_above = pd.Series(False, index=s1.index, name=col_name_above, dtype=bool)
    empty_below = pd.Series(False, index=s1.index, name=col_name_below, dtype=bool)
    try:
        s1 = pd.to_numeric(s1, errors="coerce")
        s2 = pd.to_numeric(s2, errors="coerce")
        if s1.isnull().all() or s2.isnull().all():
            local_logger.debug(
                f"{hisse_str}: Kesişim ({s1_col} vs {s2_col}) için serilerden biri tamamen NaN."
            )
            return empty_above, empty_below
        kesisim_yukari = utils.crosses_above(s1, s2).rename(col_name_above)
        kesisim_asagi = utils.crosses_below(s1, s2).rename(col_name_below)
        return kesisim_yukari, kesisim_asagi
    except Exception as e:
        local_logger.error(
            f"{hisse_str}: _calculate_series_series_crossover ({s1_col} vs {s2_col}) hatası: {e}",
            exc_info=False,
        )
        try:
            from utils.failure_tracker import log_failure

            log_failure("crossovers", f"{s1_col} vs {s2_col}", str(e))
        except Exception:
            pass
        return empty_above, empty_below


def _calculate_series_value_crossover(
    group_df: pd.DataFrame,
    s_col: str,
    value: float,
    suffix: str,
    logger_param=None,
) -> tuple[pd.Series, pd.Series] | None:
    if logger_param is None:
        logger_param = logger
    local_logger = logger_param

    if s_col not in group_df.columns:
        local_logger.debug(f"Skipped crossover {s_col} vs {value} – missing col")
        return

    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    col_name_above = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_yukari"
    col_name_below = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_asagi"
    empty_above = pd.Series(
        False, index=group_df.index, name=col_name_above, dtype=bool
    )
    empty_below = pd.Series(
        False, index=group_df.index, name=col_name_below, dtype=bool
    )
    value_series = pd.Series(
        value, index=group_df.index, name=f"sabit_deger_{str(suffix).replace('.', 'p')}"
    )
    try:
        s1 = pd.to_numeric(group_df[s_col], errors="coerce")
        if s1.isnull().all():
            local_logger.debug(
                f"{hisse_str}: Kesişim ({s_col} vs {value}) için seri tamamen NaN."
            )
            return empty_above, empty_below
        kesisim_yukari = utils.crosses_above(s1, value_series).rename(col_name_above)
        kesisim_asagi = utils.crosses_below(s1, value_series).rename(col_name_below)
        return kesisim_yukari, kesisim_asagi
    except Exception as e:
        local_logger.error(
            f"{hisse_str}: _calculate_series_value_crossover ({s_col} vs {value}) hatası: {e}",
            exc_info=False,
        )
        try:
            from utils.failure_tracker import log_failure

            log_failure("crossovers", f"{s_col} vs {value}", str(e))
        except Exception:
            pass
        return empty_above, empty_below


def _calculate_group_indicators_and_crossovers(
    _grp_df: pd.DataFrame,
    wanted_cols=None,
    df_filters: pd.DataFrame | None = None,
) -> pd.DataFrame:
    local_logger = logger
    hisse_kodu = (
        _grp_df["hisse_kodu"].iloc[0]
        if not _grp_df.empty and "hisse_kodu" in _grp_df.columns
        else "Bilinmeyen Hisse"
    )
    ta_strategy = config.TA_STRATEGY
    series_series_config = config.SERIES_SERIES_CROSSOVERS
    series_value_config = config.SERIES_VALUE_CROSSOVERS
    ozel_sutun_conf = config.OZEL_SUTUN_PARAMS
    ad_eslestirme = config.INDIKATOR_AD_ESLESTIRME
    group_df_input = _grp_df

    if wanted_cols is not None:
        extended = set(wanted_cols)
        wanted_lower = {w.lower() for w in wanted_cols}
        for raw, mapped in ad_eslestirme.items():
            if mapped.lower() in wanted_lower:
                extended.add(raw)
                extended.add(str(raw).upper())
        wanted_cols = extended

    # pandas-ta için DatetimeIndex'e çevir
    group_df_dt_indexed = group_df_input.copy()

    grouped = group_df_dt_indexed.groupby(
        "hisse_kodu" if "hisse_kodu" in group_df_dt_indexed.columns else "symbol"
    )
    if "close" in group_df_dt_indexed.columns:
        safe_set(
            group_df_dt_indexed,
            "ema_5",
            grouped["close"]
            .transform(lambda s: s.ewm(span=5, adjust=False).mean())
            .values,
        )
        safe_set(
            group_df_dt_indexed,
            "ema_20",
            grouped["close"]
            .transform(lambda s: s.ewm(span=20, adjust=False).mean())
            .values,
        )
        safe_set(
            group_df_dt_indexed,
            "ema_5_keser_ema_20_yukari",
            utils.crosses_above(
                group_df_dt_indexed["ema_5"], group_df_dt_indexed["ema_20"]
            ).values,
        )
        safe_set(
            group_df_dt_indexed,
            "ema_5_keser_ema_20_asagi",
            utils.crosses_below(
                group_df_dt_indexed["ema_5"], group_df_dt_indexed["ema_20"]
            ).values,
        )
    if "tarih" in group_df_dt_indexed.columns:
        if not pd.api.types.is_datetime64_any_dtype(group_df_dt_indexed["tarih"]):
            group_df_dt_indexed["tarih"] = pd.to_datetime(
                group_df_dt_indexed["tarih"], errors="coerce"
            )
        if not group_df_dt_indexed["tarih"].isnull().all():
            try:
                group_df_dt_indexed = group_df_dt_indexed.set_index(
                    pd.DatetimeIndex(group_df_dt_indexed["tarih"]), drop=True
                )
                if not group_df_dt_indexed.index.is_monotonic_increasing:
                    group_df_dt_indexed = group_df_dt_indexed.sort_index()
            except Exception as e_set_index:
                local_logger.error(
                    f"{hisse_kodu}: 'tarih' DatetimeIndex olarak ayarlanamadı: {e_set_index}. Orijinal RangeIndex ile devam ediliyor."
                )
                group_df_dt_indexed = (
                    group_df_input.copy()
                )  # Hata durumunda orijinaline dön
        else:
            local_logger.warning(f"{hisse_kodu}: 'tarih' sütunundaki tüm değerler NaT.")
    else:
        local_logger.error(f"{hisse_kodu}: 'tarih' sütunu bulunamadı.")

    required_ohlcv = ["open", "high", "low", "close", "volume"]
    missing_ohlcv = [
        col for col in required_ohlcv if col not in group_df_dt_indexed.columns
    ]
    if missing_ohlcv:
        local_logger.error(
            f"{hisse_kodu}: Temel OHLCV sütunları eksik: {missing_ohlcv}."
        )
        return group_df_input[
            ["hisse_kodu", "tarih"]
            + [c for c in required_ohlcv if c in group_df_input.columns]
        ].drop_duplicates()

    if ta_strategy is None:
        ta_strategy = ta.Strategy(name="empty", ta=[])

    try:
        base_list = getattr(ta_strategy, "ta", []) or []
        if wanted_cols is not None:
            filtered_indicators = [
                i
                for i in base_list
                if any(c in wanted_cols for c in i.get("col_names", []))
            ]
        else:
            filtered_indicators = base_list
        strategy_obj = ta.Strategy(
            name=getattr(ta_strategy, "name", "filtered"),
            description=getattr(ta_strategy, "description", ""),
            ta=filtered_indicators,
        )
        group_df_dt_indexed.ta.strategy(
            strategy_obj,
            timed=False,
            append=True,
            min_periods=1,
            unique=True,
        )
        if (
            "psar_long" not in group_df_dt_indexed.columns
            or "psar_short" not in group_df_dt_indexed.columns
        ):
            try:
                psar_raw = group_df_dt_indexed.ta.psar()
                if isinstance(psar_raw, pd.DataFrame):
                    psar_df = psar_raw.iloc[:, :2].copy()
                    psar_df.columns = ["psar_long", "psar_short"]
                else:
                    psar_long, psar_short = psar_raw
                    psar_df = safe_concat([psar_long, psar_short], axis=1)
                    psar_df.columns = ["psar_long", "psar_short"]
                group_df_dt_indexed = safe_concat(
                    [group_df_dt_indexed, psar_df], axis=1
                )
                safe_set(
                    group_df_dt_indexed,
                    "psar",
                    group_df_dt_indexed["psar_long"]
                    .fillna(group_df_dt_indexed["psar_short"])
                    .values,
                )
            except Exception as e_psar:
                local_logger.error(f"{hisse_kodu}: PSAR hesaplanırken hata: {e_psar}")
    except Exception as e_ta:
        local_logger.error(
            f"{hisse_kodu}: OpenBB stratejisi hatası: {e_ta}", exc_info=True
        )
        # Hata durumunda, gösterge stratejisi indikatörleri eklenemez ama devam edilir.
        group_df_dt_indexed = group_df_dt_indexed.copy()

    # Ad eşleştirmeyi DatetimeIndex'li DataFrame üzerinde yap
    if ad_eslestirme:
        # ... (önceki ad eşleştirme bloğu - aynen kalabilir) ...
        active_rename_map = {}
        df_cols_lower_map = {str(c).lower(): c for c in group_df_dt_indexed.columns}
        for pta_raw_name, cfg_target_name in ad_eslestirme.items():
            pta_raw_name_lower = str(pta_raw_name).lower()
            if pta_raw_name_lower in df_cols_lower_map:
                actual_col_name_in_df = df_cols_lower_map[pta_raw_name_lower]
                if (
                    actual_col_name_in_df != cfg_target_name
                    and cfg_target_name not in group_df_dt_indexed.columns
                ):
                    active_rename_map[actual_col_name_in_df] = cfg_target_name
        if active_rename_map:
            group_df_dt_indexed.rename(
                columns=active_rename_map, inplace=True, errors="ignore"
            )
            local_logger.debug(
                f"{hisse_kodu}: İndikatör adları eşleştirildi (config): {active_rename_map}"
            )

    # Şimdi tüm hesaplamaların (özel ve kesişimler) yapılacağı RangeIndex'li DataFrame'i hazırlayalım.
    # Bu DataFrame, pandas-ta tarafından hesaplanan indikatörleri de içermeli.
    # group_df_input (RangeIndex, 'tarih' sütunlu, OHLCV)
    # group_df_dt_indexed (DatetimeIndex, 'tarih' SÜTUNU YOK, OHLCV +
    # pandas-ta indikatörleri)

    # En temiz yol: group_df_dt_indexed'in indeksini sıfırlayıp 'tarih' sütununu geri getirmek
    # ve orijinal group_df_input ile birleştirmek (sadece yeni eklenen
    # sütunları almak için).

    df_final_group = (
        group_df_input.copy()
    )  # Temel olarak orijinal df'i alalım (RangeIndex, 'tarih' sütunlu)
    seen_names = set(df_final_group.columns)

    # pandas-ta ile hesaplanan sütunları (DatetimeIndex'li df'ten) RangeIndex'li df_final_group'a aktar
    # İndeksler farklı olduğu için doğrudan merge yerine, değerleri .values ile atamak daha güvenli olabilir,
    # ancak her iki df'in de aynı sayıda satıra sahip olması ve sıralı olması gerekir.
    # group_df_sorted_range_indexed en başta oluşturulmuştu.

    # pandas-ta'nın eklediği yeni sütunları alalım (OHLCV hariç)
    new_ta_cols_list = [
        col
        for col in group_df_dt_indexed.columns
        if col not in group_df_input.columns and col not in required_ohlcv
    ]
    valid_cols = {
        c: group_df_dt_indexed[c].values
        for c in new_ta_cols_list
        if len(group_df_dt_indexed[c]) == len(df_final_group)
    }
    if valid_cols:
        for c, vals in valid_cols.items():
            safe_set(df_final_group, c, vals)

    # Bazı durumlarda OpenBB stratejisinden beklenen indikatörler veri
    # yetersizliği nedeniyle oluşmayabilir. Filtrelerin sorunsuz çalışması için
    # eksik olan temel bazı indikatörleri manuel olarak üretelim.

    manual_cols = {}
    if (
        set(wanted_cols or []) & {"ITS_9", "its_9", "ichimoku_conversionline"}
        and "ITS_9" not in df_final_group.columns
        and {"high", "low", "close"}.issubset(df_final_group.columns)
    ):
        try:
            ich_df, _ = obb_ichimoku(
                df_final_group["high"],
                df_final_group["low"],
                df_final_group["close"],
            )
            if ich_df is not None and "ITS_9" in ich_df:
                target = config.INDIKATOR_AD_ESLESTIRME.get(
                    "ITS_9", "ichimoku_conversionline"
                )
                manual_cols[target] = ich_df["ITS_9"]
                local_logger.debug(
                    f"{hisse_kodu}: 'ITS_9' sütunu manuel olarak hesaplandı."
                )
        except Exception as e_ich:
            local_logger.error(
                f"{hisse_kodu}: 'ITS_9' hesaplanırken hata: {e_ich}",
                exc_info=False,
            )
    if "ema_8" not in df_final_group.columns and "close" in df_final_group.columns:
        manual_cols["ema_8"] = df_final_group["close"].ewm(span=8, adjust=False).mean()
        local_logger.debug(f"{hisse_kodu}: 'ema_8' sütunu manuel olarak hesaplandı.")

    if "tema_20" not in df_final_group.columns and "close" in df_final_group.columns:
        manual_cols["tema_20"] = _tema20(df_final_group["close"])
        local_logger.debug(f"{hisse_kodu}: 'tema_20' sütunu manuel olarak hesaplandı.")

    for period in config.GEREKLI_MA_PERIYOTLAR:
        safe_ma(df_final_group, period, "sma", local_logger)
        safe_ma(df_final_group, period, "ema", local_logger)

    if (
        "momentum_10" not in df_final_group.columns
        and "close" in df_final_group.columns
    ):
        manual_cols["momentum_10"] = df_final_group["close"].diff(periods=10)
        local_logger.debug(
            f"{hisse_kodu}: 'momentum_10' sütunu manuel olarak hesaplandı."
        )

    if "rsi_14" not in df_final_group.columns and "close" in df_final_group.columns:
        try:
            manual_cols["rsi_14"] = obb_rsi(df_final_group["close"], length=14)
            local_logger.debug(
                f"{hisse_kodu}: 'rsi_14' sütunu manuel olarak hesaplandı."
            )
        except Exception as e_rsi:
            local_logger.error(
                f"{hisse_kodu}: rsi_14 hesaplanırken hata: {e_rsi}", exc_info=False
            )

    if (
        {"macd_line", "macd_signal"} - set(df_final_group.columns)
    ) and "close" in df_final_group.columns:
        try:
            macd_df = obb_macd(df_final_group["close"], fast=12, slow=26, signal=9)
            if isinstance(macd_df, pd.DataFrame):
                if "macd_line" not in df_final_group.columns:
                    manual_cols["macd_line"] = macd_df.iloc[:, 0]
                if "macd_signal" not in df_final_group.columns:
                    manual_cols["macd_signal"] = macd_df.iloc[:, 1]
            local_logger.debug(
                f"{hisse_kodu}: 'macd_line' ve 'macd_signal' sütunları manuel olarak hesaplandı."
            )
        except Exception as e_macd:
            local_logger.error(
                f"{hisse_kodu}: macd hesaplanırken hata: {e_macd}", exc_info=False
            )

    if (
        {"stochrsi_k", "stochrsi_d"} - set(df_final_group.columns)
    ) and "close" in df_final_group.columns:
        try:
            stoch_df = ta.stochrsi(df_final_group["close"], length=14)
            if isinstance(stoch_df, pd.DataFrame):
                if "stochrsi_k" not in df_final_group.columns:
                    manual_cols["stochrsi_k"] = stoch_df.iloc[:, 0]
                if "stochrsi_d" not in df_final_group.columns:
                    manual_cols["stochrsi_d"] = stoch_df.iloc[:, 1]
            local_logger.debug(
                f"{hisse_kodu}: 'stochrsi_k/d' sütunları manuel olarak hesaplandı."
            )
        except Exception as e_stoch:
            local_logger.error(
                f"{hisse_kodu}: stochrsi hesaplanırken hata: {e_stoch}", exc_info=False
            )

    if manual_cols:
        for alias, vals in manual_cols.items():
            add_series(df_final_group, alias, vals, seen_names)

    # Özel Sütunlar (df_final_group üzerinde, zaten RangeIndex'li)
    for sutun_conf in ozel_sutun_conf:
        yeni_sutun_adi = sutun_conf["name"]
        fonksiyon_adi_str = sutun_conf["function"]
        parametreler = sutun_conf.get("params", {})
        try:
            fonksiyon = globals().get(fonksiyon_adi_str)
            if fonksiyon:
                result_series = fonksiyon(
                    df_final_group.copy(), **parametreler
                )  # Fonksiyona kopya ver
                if result_series is not None and len(result_series) == len(
                    df_final_group
                ):
                    add_series(
                        df_final_group, yeni_sutun_adi, result_series.values, seen_names
                    )
                else:
                    add_series(
                        df_final_group,
                        yeni_sutun_adi,
                        np.full(len(df_final_group), np.nan),
                        seen_names,
                    )
            else:
                add_series(
                    df_final_group,
                    yeni_sutun_adi,
                    np.full(len(df_final_group), np.nan),
                    seen_names,
                )
                local_logger.error(
                    f"{hisse_kodu}: Özel sütun için '{fonksiyon_adi_str}' fonksiyonu bulunamadı."
                )
        except Exception as e_ozel:
            add_series(
                df_final_group,
                yeni_sutun_adi,
                np.full(len(df_final_group), np.nan),
                seen_names,
            )
            local_logger.error(
                f"{hisse_kodu}: Özel sütun '{yeni_sutun_adi}' hesaplanırken hata: {e_ozel}",
                exc_info=False,
            )

    # Kesişimler (df_final_group üzerinde)
    for s1_c, s2_c, c_above, c_below in series_series_config:
        result = _calculate_series_series_crossover(
            df_final_group.copy(), s1_c, s2_c, c_above, c_below, local_logger
        )
        if result is None:
            continue
        kesisim_yukari, kesisim_asagi = result
        if len(kesisim_yukari) == len(df_final_group):
            add_series(df_final_group, c_above, kesisim_yukari.values, seen_names)
        else:
            add_series(
                df_final_group,
                c_above,
                np.full(len(df_final_group), np.nan),
                seen_names,
            )
        if len(kesisim_asagi) == len(df_final_group):
            add_series(df_final_group, c_below, kesisim_asagi.values, seen_names)
        else:
            add_series(
                df_final_group,
                c_below,
                np.full(len(df_final_group), np.nan),
                seen_names,
            )

    for s_c, val, suff in series_value_config:
        result = _calculate_series_value_crossover(
            df_final_group.copy(), s_c, val, suff, local_logger
        )
        if result is None:
            continue
        kesisim_yukari, kesisim_asagi = result
        if len(kesisim_yukari) == len(df_final_group):
            add_series(
                df_final_group,
                kesisim_yukari.name,
                kesisim_yukari.values,
                seen_names,
            )
        else:
            add_series(
                df_final_group,
                kesisim_yukari.name,
                np.full(len(df_final_group), np.nan),
                seen_names,
            )
        if len(kesisim_asagi) == len(df_final_group):
            add_series(
                df_final_group,
                kesisim_asagi.name,
                kesisim_asagi.values,
                seen_names,
            )
        else:
            add_series(
                df_final_group,
                kesisim_asagi.name,
                np.full(len(df_final_group), np.nan),
                seen_names,
            )

    auto_names = load_ema_close_crossovers()
    if auto_names:
        try:
            add_crossovers(df_final_group, auto_names)
        except ValueError as e_auto:
            local_logger.error(f"{hisse_kodu}: {e_auto}")
    if (
        "bbm_20_2" in df_final_group.columns
        and "BBM_20_2" not in df_final_group.columns
    ):
        add_series(df_final_group, "BBM_20_2", df_final_group["bbm_20_2"], seen_names)

    df_final_group = df_final_group.loc[:, ~df_final_group.columns.duplicated()]
    return df_final_group


def hesapla_teknik_indikatorler_ve_kesisimler(
    df_islenmis_veri: pd.DataFrame,
    wanted_cols=None,
    df_filters: pd.DataFrame | None = None,
    logger_param=None,
) -> pd.DataFrame | None:
    if logger_param is None:
        logger_param = logger
    ana_logger = logger_param
    ana_logger.info(
        "Teknik indikatörler ve kesişim sinyalleri hesaplanmaya başlanıyor..."
    )

    if df_islenmis_veri is None or df_islenmis_veri.empty:
        ana_logger.critical(
            "İndikatör hesaplama için işlenmiş veri (df_islenmis_veri) boş veya None."
        )
        return None

    gerekli_sutunlar = ["tarih", "open", "high", "low", "close", "volume", "hisse_kodu"]
    eksik_sutunlar = [
        col for col in gerekli_sutunlar if col not in df_islenmis_veri.columns
    ]
    if eksik_sutunlar:
        ana_logger.critical(
            f"İndikatör hesaplama ana fonksiyonuna gelen DataFrame'de temel sütunlar eksik: {eksik_sutunlar}."
        )
        return None

    # NaN ön temizlik: OHLCV kolonlarındaki boşlukları 3 satıra kadar ileri taşı
    ind_cols = [
        c
        for c in ["open", "high", "low", "close", "volume"]
        if c in df_islenmis_veri.columns
    ]
    if ind_cols:
        df_islenmis_veri[ind_cols] = df_islenmis_veri[ind_cols].ffill(limit=3)

    _ekle_psar(df_islenmis_veri)

    series_series_crossovers = config.SERIES_SERIES_CROSSOVERS
    series_value_crossovers = config.SERIES_VALUE_CROSSOVERS

    filtre_df = df_filters
    if filtre_df is None:
        try:
            filtre_df = normalize_filtre_kodu(
                pd.read_csv(config.FILTRE_DOSYA_YOLU, sep=";", engine="python")
            )
        except Exception:
            filtre_df = pd.DataFrame()

    if wanted_cols is None:
        csv_str = filtre_df.to_csv(index=False) if not filtre_df.empty else ""
        wanted_cols = utils.extract_columns_from_filters_cached(
            csv_str,
            tuple(series_series_crossovers),
            tuple(series_value_crossovers),
        )

    results_list = []
    groupby_obj = df_islenmis_veri.groupby("hisse_kodu", group_keys=False)

    total_stocks = len(df_islenmis_veri["hisse_kodu"].unique())
    current_processed_count_main = 0

    for (
        hisse_kodu,
        group_df_original,
    ) in (
        groupby_obj
    ):  # group_df_original zaten 'tarih'e göre sıralı geliyor (preprocessor'dan)
        current_processed_count_main += 1
        # _calculate_group_indicators_and_crossovers fonksiyonuna RangeIndex'li ve 'tarih' sütunlu df gönderiyoruz.
        # Bu fonksiyon içinde DatetimeIndex'e çevrilip, sonra tekrar RangeIndex'e
        # ve 'tarih' sütununa sahip olarak dönüyor.
        group_df_for_calc = group_df_original.reset_index(
            drop=True
        )  # Her ihtimale karşı indeksi sıfırla

        step = max(1, int(total_stocks * PCT_STEP / 100))
        msg = f"({current_processed_count_main}/{total_stocks}) {hisse_kodu} için indikatör hesaplama..."
        if (
            current_processed_count_main % step == 0
            or current_processed_count_main == 1
            or current_processed_count_main == total_stocks
        ):
            ana_logger.info(msg)
        else:
            ana_logger.debug(msg)

        calculated_group = _calculate_group_indicators_and_crossovers(
            group_df_for_calc, wanted_cols, filtre_df
        )
        if calculated_group is not None and not calculated_group.empty:
            group_df = calculated_group
            dup_cols = group_df.columns[group_df.columns.duplicated()]
            if dup_cols.any():
                ana_logger.warning(
                    f"{hisse_kodu}: yinelenen kolonlar atıldı -> {dup_cols.tolist()}"
                )
                group_df = group_df.loc[:, ~group_df.columns.duplicated()]

            if group_df.index.duplicated().any():
                ana_logger.warning(f"{hisse_kodu}: yinelenen satır index'i silindi")
                group_df = group_df[~group_df.index.duplicated()]

            group_df.reset_index(drop=True, inplace=True)
            results_list.append(
                group_df
            )  # group_df zaten RangeIndex'li ve 'tarih' sütunlu dönmeli
        else:
            ana_logger.warning(
                f"{hisse_kodu} için indikatör hesaplama sonucu boş veya None döndü."
            )

    if not results_list:
        ana_logger.error(
            "Hiçbir hisse için geçerli indikatör sonucu üretilemedi. Son DataFrame boş olacak."
        )
        return pd.DataFrame()

    try:
        df_sonuc = safe_concat(results_list, ignore_index=True)

        if "tarih" in df_sonuc.columns and not pd.api.types.is_datetime64_any_dtype(
            df_sonuc["tarih"]
        ):
            df_sonuc["tarih"] = pd.to_datetime(df_sonuc["tarih"], errors="coerce")
        elif "tarih" not in df_sonuc.columns:
            ana_logger.error(
                "Birleştirilmiş sonuç DataFrame'inde 'tarih' sütunu bulunmuyor!"
            )

        df_sonuc.sort_values(
            by=["hisse_kodu", "tarih"], inplace=True, na_position="first"
        )
        df_sonuc.reset_index(drop=True, inplace=True)
        df_sonuc = df_sonuc.loc[:, ~df_sonuc.columns.duplicated()]

        ana_logger.info(
            f"Tüm {current_processed_count_main} hisse için indikatör ve kesişim hesaplamaları tamamlandı. Son DataFrame boyutu: {df_sonuc.shape}"
        )
        if not df_sonuc.empty:
            ana_logger.info(
                f"Filtrelemeye gönderilecek DataFrame sütunları ({len(df_sonuc.columns)} adet): {df_sonuc.columns.tolist()}"
            )
        return df_sonuc
    except Exception as e_concat:
        ana_logger.critical(
            f"Hesaplanan indikatörler birleştirilirken KRİTİK HATA: {e_concat}",
            exc_info=True,
        )
        return pd.DataFrame()
