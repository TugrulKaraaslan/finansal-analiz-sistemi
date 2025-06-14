# indicator_calculator.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Teknik İndikatörler ve Kesişim Sinyalleri Hesaplama
# Tuğrul Karaaslan & Gemini
# Tarih: 19 Mayıs 2025 (Tüm özel fonksiyonlar eklendi, reset_index düzeltildi, filtre uyumu artırıldı v2)

import pandas as pd
import pandas.errors
import numpy as np
import warnings

# numpy>=2.0 paketlerinde `NaN` sabiti kaldırıldı. pandas_ta halen bu adı
# kullandığından import sırasında hata oluşabiliyor. Eğer `np.NaN` mevcut
# değilse `np.nan` değerini aynı isimle tanımlayarak uyumluluk sağlanır.
if not hasattr(np, "NaN"):
    np.NaN = np.nan

import pandas_ta as ta
from pandas_ta import psar as ta_psar
import config
import utils

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

try:
    from logger_setup import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning("logger_setup.py bulunamadı, indicator_calculator.py standart logging kullanıyor.")

# --- Yeni Özel İndikatör Fonksiyonları (Filtrelerle Uyum İçin) ---

def _calculate_change_percent(group_df: pd.DataFrame, period: int, price_col: str = 'close', output_col_name: str = None) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    
    effective_output_col_name = output_col_name
    if not effective_output_col_name:
        if period == 5 and price_col == 'close': effective_output_col_name = "change_1w_percent"
        elif (period == 20 or period == 21 or period == 22) and price_col == 'close': effective_output_col_name = "change_1m_percent"
        elif period == 1 and price_col == 'close': effective_output_col_name = "change_1h_percent" # Aslında günlük
        elif period == 1 and price_col == 'volume': effective_output_col_name = "volume_change_percent_1d"
        else: effective_output_col_name = f"{price_col}_change_{period}bar_percent"

    try:
        if price_col not in group_df.columns:
            logger.debug(f"{hisse_str}: {effective_output_col_name} için '{price_col}' sütunu bulunamadı.")
            return pd.Series(np.nan, index=group_df.index, name=effective_output_col_name)
        
        if len(group_df) < period + 1:
            logger.debug(f"{hisse_str}: {effective_output_col_name} hesaplamak için yeterli veri yok ({len(group_df)} satır, {period} periyot gerekli).")
            return pd.Series(np.nan, index=group_df.index, name=effective_output_col_name)
            
        change = group_df[price_col].pct_change(periods=period) * 100
        return change.round(2).rename(effective_output_col_name)
    except Exception as e:
        logger.error(f"{hisse_str}: {effective_output_col_name} (periyot: {period}, sütun: {price_col}) hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=effective_output_col_name)

def _calculate_sma(group_df: pd.DataFrame, period: int, data_col: str) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = f"{data_col}_{period}_sma"
    try:
        if data_col not in group_df.columns:
            logger.debug(f"{hisse_str}: {sutun_adi} için '{data_col}' sütunu bulunamadı.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        if len(group_df) < period:
             logger.debug(f"{hisse_str}: {sutun_adi} hesaplamak için yeterli veri yok ({len(group_df)} satır, {period} periyot gerekli).")
             return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        return group_df[data_col].rolling(window=period, min_periods=period).mean().round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: {sutun_adi} hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _get_previous_bar_value(group_df: pd.DataFrame, data_col: str, shift_by: int = 1) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = f"prev_{data_col}_{shift_by}"
    try:
        if data_col not in group_df.columns:
            logger.debug(f"{hisse_str}: {sutun_adi} için '{data_col}' sütunu bulunamadı.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        return group_df[data_col].shift(shift_by).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: {sutun_adi} hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_combined_psar(group_df: pd.DataFrame) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = "psar"
    try:
        if 'psar_long' in group_df.columns and 'psar_short' in group_df.columns:
            combined_psar = group_df['psar_long'].fillna(group_df['psar_short'])
            return combined_psar.rename(sutun_adi)
        else:
            logger.debug(f"{hisse_str}: Birleşik PSAR için 'psar_long' veya 'psar_short' sütunları bulunamadı.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: Birleşik PSAR hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_percentage_from_period_high_low(group_df: pd.DataFrame, price_col: str, period: int, mode: str) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    
    if period == 252 and mode == 'high': sutun_adi = "percentage_from_52w_high"
    elif period == 252 and mode == 'low': sutun_adi = "percentage_from_52w_low"
    else:
        sutun_adi = f"percentage_from_{period}bar_{mode}"

    try:
        if price_col not in group_df.columns:
            logger.debug(f"{hisse_str}: {sutun_adi} için '{price_col}' sütunu eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        
        if len(group_df) < period:
             logger.debug(f"{hisse_str}: {sutun_adi} hesaplamak için yeterli veri yok ({len(group_df)} satır, {period} periyot gerekli).")
             return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

        if mode == 'high':
            period_extreme = group_df[price_col].rolling(window=period, min_periods=period).max()
            percentage = ((group_df[price_col] - period_extreme) / period_extreme.replace(0, np.nan)) * 100
        elif mode == 'low':
            period_extreme = group_df[price_col].rolling(window=period, min_periods=period).min()
            percentage = ((group_df[price_col] - period_extreme) / period_extreme.replace(0, np.nan)) * 100
        else:
            logger.warning(f"{hisse_str}: {sutun_adi} için geçersiz mod: {mode}")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        
        return percentage.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: {sutun_adi} hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_relative_volume(group_df: pd.DataFrame, window: int, col_name_prefix: str = 'volume') -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = next((item['name'] for item in config.OZEL_SUTUN_PARAMS if item['function'] == '_calculate_relative_volume'), 'relative_volume_default')
    try:
        vol_column = col_name_prefix
        if vol_column not in group_df.columns:
            logger.debug(f"{hisse_str}: Relative Volume ({sutun_adi}) için '{vol_column}' sütunu bulunamadı.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        if len(group_df) < window:
            logger.debug(f"{hisse_str}: {sutun_adi} hesaplamak için yeterli veri yok ({len(group_df)} satır, {window} periyot gerekli).")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        avg_vol = group_df[vol_column].rolling(window=window, min_periods=window).mean()
        relative_volume_series = group_df[vol_column] / avg_vol.replace(0, np.nan)
        return relative_volume_series.rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: Relative Volume ({sutun_adi}, {window}) hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_volume_price(group_df: pd.DataFrame, col_name_prefix_vol: str = 'volume', col_name_prefix_price: str = 'close') -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = next((item['name'] for item in config.OZEL_SUTUN_PARAMS if item['function'] == '_calculate_volume_price'), 'volume_price_default')
    try:
        if col_name_prefix_vol not in group_df.columns or col_name_prefix_price not in group_df.columns:
            logger.debug(f"{hisse_str}: Hacim*Fiyat ({sutun_adi}) için '{col_name_prefix_vol}' veya '{col_name_prefix_price}' sütunu eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        return (group_df[col_name_prefix_vol] * group_df[col_name_prefix_price]).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: Hacim*Fiyat ({sutun_adi}) hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)


def safe_ma(df: pd.DataFrame, n: int, kind: str = "sma", logger_param=None) -> None:
    """Eksikse basit veya üssel hareketli ortalama kolonu ekler."""
    local_logger = logger_param or logger
    col = f"{kind}_{n}"
    if col in df.columns or "close" not in df.columns:
        return
    try:
        if kind == "sma":
            df[col] = df["close"].rolling(window=n, min_periods=1).mean()
        else:
            df[col] = df["close"].ewm(span=n, adjust=False, min_periods=1).mean()
        local_logger.debug(f"'{col}' sütunu safe_ma ile eklendi.")
    except Exception as e:
        local_logger.error(f"'{col}' hesaplanırken hata: {e}", exc_info=False)


def safe_get(df: pd.DataFrame, col: str) -> pd.Series | None:
    """DataFrame'den güvenli sütun erişimi yapar."""
    if col not in df.columns:
        logger.debug(f"{col} eksik – crossover atlandı")
        return None
    return df[col]

def _ekle_psar(df: pd.DataFrame) -> None:
    """PSAR kolonlarını hesaplar ve ekler."""
    gerekli = ["high", "low", "close"]
    if any(c not in df.columns for c in gerekli):
        logger.debug("PSAR hesaplamak için gerekli sütunlar eksik")
        return
    try:
        psar_up, psar_dn = ta_psar(high=df["high"], low=df["low"], close=df["close"])
        df["psar_long"] = psar_up
        df["psar_short"] = psar_dn
        df["psar"] = np.where(df["psar_long"].notna(), df["psar_long"], df["psar_short"])
    except Exception as e:
        logger.error(f"PSAR hesaplanırken hata: {e}")

def _calculate_classicpivots_1h_p(group_df: pd.DataFrame) -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = "classicpivots_1h_p"
    try:
        gerekli = ['high', 'low', 'close']
        if any(col not in group_df.columns for col in gerekli):
            logger.debug(f"{hisse_str}: {sutun_adi} için gerekli sütunlar eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        pivot = (group_df['high'] + group_df['low'] + group_df['close']) / 3
        return pivot.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: {sutun_adi} hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_change_from_open(group_df: pd.DataFrame, col_name_open: str = 'open', col_name_close: str = 'close') -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = next((item['name'] for item in config.OZEL_SUTUN_PARAMS if item['function'] == '_calculate_change_from_open'), 'change_from_open_percent_default')
    try:
        if col_name_open not in group_df.columns or col_name_close not in group_df.columns:
            logger.debug(f"{hisse_str}: Açılıştan değişim ({sutun_adi}) için '{col_name_open}' veya '{col_name_close}' sütunu eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        change = (group_df[col_name_close] - group_df[col_name_open]) / group_df[col_name_open].replace(0, np.nan) * 100
        return change.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: Açılıştan değişim ({sutun_adi}) hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_percentage_from_all_time_high(group_df: pd.DataFrame, price_col: str = 'high') -> pd.Series:
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    sutun_adi = next((item['name'] for item in config.OZEL_SUTUN_PARAMS if item['function'] == '_calculate_percentage_from_all_time_high'), 'percentage_from_ath_default')
    try:
        if price_col not in group_df.columns:
            logger.debug(f"{hisse_str}: ATH'den yüzde ({sutun_adi}) için '{price_col}' sütunu eksik.")
            return pd.Series(np.nan, index=group_df.index, name=sutun_adi)
        all_time_high = group_df[price_col].expanding(min_periods=1).max()
        percentage_from_ath = ((group_df[price_col] - all_time_high) / all_time_high.replace(0, np.nan)) * 100
        return percentage_from_ath.round(2).rename(sutun_adi)
    except Exception as e:
        logger.error(f"{hisse_str}: ATH'den yüzde ({sutun_adi}) hesaplanırken hata: {e}", exc_info=False)
        return pd.Series(np.nan, index=group_df.index, name=sutun_adi)

def _calculate_series_series_crossover(
    group_df: pd.DataFrame,
    s1_col: str,
    s2_col: str,
    col_name_above: str,
    col_name_below: str,
    logger_param=None,
) -> tuple[pd.Series, pd.Series] | None:
    local_logger = logger_param or logger

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
        return empty_above, empty_below

def _calculate_series_value_crossover(
    group_df: pd.DataFrame,
    s_col: str,
    value: float,
    suffix: str,
    logger_param=None,
) -> tuple[pd.Series, pd.Series] | None:
    local_logger = logger_param or logger

    if s_col not in group_df.columns:
        local_logger.debug(
            f"Skipped crossover {s_col} vs {value} – missing col"
        )
        return

    hisse_str = (
        group_df["hisse_kodu"].iloc[0]
        if not group_df.empty and "hisse_kodu" in group_df.columns
        else "Bilinmeyen Hisse"
    )
    col_name_above = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_yukari"
    col_name_below = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_asagi"
    empty_above = pd.Series(False, index=group_df.index, name=col_name_above, dtype=bool)
    empty_below = pd.Series(False, index=group_df.index, name=col_name_below, dtype=bool)
    value_series = pd.Series(value, index=group_df.index, name=f"sabit_deger_{str(suffix).replace('.', 'p')}")
    try:
        s1 = pd.to_numeric(group_df[s_col], errors='coerce')
        if s1.isnull().all():
            local_logger.debug(f"{hisse_str}: Kesişim ({s_col} vs {value}) için seri tamamen NaN.")
            return empty_above, empty_below
        kesisim_yukari = utils.crosses_above(s1, value_series).rename(col_name_above)
        kesisim_asagi = utils.crosses_below(s1, value_series).rename(col_name_below)
        return kesisim_yukari, kesisim_asagi
    except Exception as e:
        local_logger.error(f"{hisse_str}: _calculate_series_value_crossover ({s_col} vs {value}) hatası: {e}", exc_info=False)
        return empty_above, empty_below

def _calculate_group_indicators_and_crossovers(hisse_kodu: str,
                                               group_df_input: pd.DataFrame, # Bu her zaman RangeIndex ve 'tarih' sütunlu gelmeli
                                               ta_strategy: ta.Strategy,
                                               series_series_config: list,
                                               series_value_config: list,
                                               ozel_sutun_conf: list,
                                               ad_eslestirme: dict,
                                               logger_param=None) -> pd.DataFrame:
    local_logger = logger_param or logger
    
    # pandas-ta için DatetimeIndex'e çevir
    group_df_dt_indexed = group_df_input.copy()
    if 'tarih' in group_df_dt_indexed.columns:
        if not pd.api.types.is_datetime64_any_dtype(group_df_dt_indexed['tarih']):
            group_df_dt_indexed['tarih'] = pd.to_datetime(group_df_dt_indexed['tarih'], errors='coerce')
        if not group_df_dt_indexed['tarih'].isnull().all():
            try:
                group_df_dt_indexed = group_df_dt_indexed.set_index(
                    pd.DatetimeIndex(group_df_dt_indexed['tarih']), drop=True
                )
                if not group_df_dt_indexed.index.is_monotonic_increasing: group_df_dt_indexed = group_df_dt_indexed.sort_index()
            except Exception as e_set_index:
                local_logger.error(f"{hisse_kodu}: 'tarih' DatetimeIndex olarak ayarlanamadı: {e_set_index}. Orijinal RangeIndex ile devam ediliyor.")
                group_df_dt_indexed = group_df_input.copy() # Hata durumunda orijinaline dön
        else: local_logger.warning(f"{hisse_kodu}: 'tarih' sütunundaki tüm değerler NaT.")
    else: local_logger.error(f"{hisse_kodu}: 'tarih' sütunu bulunamadı.")

    required_ohlcv = ['open', 'high', 'low', 'close', 'volume']
    missing_ohlcv = [col for col in required_ohlcv if col not in group_df_dt_indexed.columns]
    if missing_ohlcv:
        local_logger.error(f"{hisse_kodu}: Temel OHLCV sütunları eksik: {missing_ohlcv}.")
        return group_df_input[['hisse_kodu', 'tarih'] + [c for c in required_ohlcv if c in group_df_input.columns]].drop_duplicates()

    if ta_strategy is None:
        ta_strategy = ta.Strategy(name="empty", ta=[])

    try:
        try:
            filtre_df = pd.read_csv(config.FILTRE_DOSYA_YOLU, sep=';', engine='python')
        except Exception:
            filtre_df = pd.DataFrame()
        wanted = utils.extract_columns_from_filters(
            filtre_df,
            series_series_config,
            series_value_config,
        )
        base_list = getattr(ta_strategy, 'ta', []) or []
        filtered_indicators = [i for i in base_list if any(c in wanted for c in i.get('col_names', []))]
        strategy_obj = ta.Strategy(name=getattr(ta_strategy, 'name', 'filtered'), description=getattr(ta_strategy, 'description', ''), ta=filtered_indicators)
        group_df_dt_indexed.ta.strategy(strategy_obj, timed=False, append=True, min_periods=1)
        if "psar_long" not in group_df_dt_indexed.columns or "psar_short" not in group_df_dt_indexed.columns:
            psar_df = group_df_dt_indexed.ta.psar()[["PSARl_0", "PSARs_0"]]
            psar_df.columns = ["psar_long", "psar_short"]
            group_df_dt_indexed = pd.concat([group_df_dt_indexed, psar_df], axis=1)
    except Exception as e_ta:
        local_logger.error(f"{hisse_kodu}: pandas-ta stratejisi hatası: {e_ta}", exc_info=True)
        # Hata durumunda, pandas-ta indikatörleri eklenemez ama devam edilir.
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
                if actual_col_name_in_df != cfg_target_name and cfg_target_name not in group_df_dt_indexed.columns:
                    active_rename_map[actual_col_name_in_df] = cfg_target_name
        if active_rename_map:
            group_df_dt_indexed.rename(columns=active_rename_map, inplace=True, errors='ignore')
            local_logger.debug(f"{hisse_kodu}: İndikatör adları eşleştirildi (config): {active_rename_map}")


    # Şimdi tüm hesaplamaların (özel ve kesişimler) yapılacağı RangeIndex'li DataFrame'i hazırlayalım.
    # Bu DataFrame, pandas-ta tarafından hesaplanan indikatörleri de içermeli.
    # group_df_input (RangeIndex, 'tarih' sütunlu, OHLCV)
    # group_df_dt_indexed (DatetimeIndex, 'tarih' SÜTUNU YOK, OHLCV + pandas-ta indikatörleri)

    # En temiz yol: group_df_dt_indexed'in indeksini sıfırlayıp 'tarih' sütununu geri getirmek
    # ve orijinal group_df_input ile birleştirmek (sadece yeni eklenen sütunları almak için).
    
    df_final_group = group_df_input.copy() # Temel olarak orijinal df'i alalım (RangeIndex, 'tarih' sütunlu)

    # pandas-ta ile hesaplanan sütunları (DatetimeIndex'li df'ten) RangeIndex'li df_final_group'a aktar
    # İndeksler farklı olduğu için doğrudan merge yerine, değerleri .values ile atamak daha güvenli olabilir,
    # ancak her iki df'in de aynı sayıda satıra sahip olması ve sıralı olması gerekir.
    # group_df_sorted_range_indexed en başta oluşturulmuştu.
    
    # pandas-ta'nın eklediği yeni sütunları alalım (OHLCV hariç)
    new_ta_cols_list = [col for col in group_df_dt_indexed.columns if col not in group_df_input.columns and col not in required_ohlcv]
    valid_cols = {
        c: group_df_dt_indexed[c].values
        for c in new_ta_cols_list
        if len(group_df_dt_indexed[c]) == len(df_final_group)
    }
    if valid_cols:
        df_final_group = df_final_group.join(
            pd.DataFrame(valid_cols, index=df_final_group.index), how="left"
        )

    # Bazı durumlarda pandas-ta stratejisinden beklenen indikatörler veri
    # yetersizliği nedeniyle oluşmayabilir. Filtrelerin sorunsuz çalışması için
    # eksik olan temel bazı indikatörleri manuel olarak üretelim.

    manual_cols = {}
    if 'ema_8' not in df_final_group.columns and 'close' in df_final_group.columns:
        manual_cols['ema_8'] = df_final_group['close'].ewm(span=8, adjust=False).mean()
        local_logger.debug(f"{hisse_kodu}: 'ema_8' sütunu manuel olarak hesaplandı.")

    for period in config.GEREKLI_MA_PERIYOTLAR:
        safe_ma(df_final_group, period, 'sma', local_logger)
        safe_ma(df_final_group, period, 'ema', local_logger)

    if 'momentum_10' not in df_final_group.columns and 'close' in df_final_group.columns:
        manual_cols['momentum_10'] = df_final_group['close'].diff(periods=10)
        local_logger.debug(f"{hisse_kodu}: 'momentum_10' sütunu manuel olarak hesaplandı.")

    if manual_cols:
        df_final_group = pd.concat([df_final_group, pd.DataFrame(manual_cols, index=df_final_group.index)], axis=1)

    # Özel Sütunlar (df_final_group üzerinde, zaten RangeIndex'li)
    new_cols = {}
    for sutun_conf in ozel_sutun_conf:
        yeni_sutun_adi = sutun_conf['name']
        fonksiyon_adi_str = sutun_conf['function']
        parametreler = sutun_conf.get('params', {})
        try:
            fonksiyon = globals().get(fonksiyon_adi_str)
            if fonksiyon:
                result_series = fonksiyon(df_final_group.copy(), **parametreler)  # Fonksiyona kopya ver
                if result_series is not None and len(result_series) == len(df_final_group):
                    new_cols[yeni_sutun_adi] = result_series.values
                else:
                    new_cols[yeni_sutun_adi] = np.full(len(df_final_group), np.nan)
            else:
                new_cols[yeni_sutun_adi] = np.full(len(df_final_group), np.nan)
                local_logger.error(f"{hisse_kodu}: Özel sütun için '{fonksiyon_adi_str}' fonksiyonu bulunamadı.")
        except Exception as e_ozel:
            new_cols[yeni_sutun_adi] = np.full(len(df_final_group), np.nan)
            local_logger.error(f"{hisse_kodu}: Özel sütun '{yeni_sutun_adi}' hesaplanırken hata: {e_ozel}", exc_info=False)
    if new_cols:
        df_final_group = pd.concat([df_final_group, pd.DataFrame(new_cols, index=df_final_group.index)], axis=1)


    # Kesişimler (df_final_group üzerinde)
    new_cols = {}
    for s1_c, s2_c, c_above, c_below in series_series_config:
        result = _calculate_series_series_crossover(
            df_final_group.copy(), s1_c, s2_c, c_above, c_below, local_logger
        )
        if result is None:
            continue
        kesisim_yukari, kesisim_asagi = result
        if len(kesisim_yukari) == len(df_final_group):
            new_cols[c_above] = kesisim_yukari.values
        else:
            new_cols[c_above] = np.full(len(df_final_group), np.nan)
        if len(kesisim_asagi) == len(df_final_group):
            new_cols[c_below] = kesisim_asagi.values
        else:
            new_cols[c_below] = np.full(len(df_final_group), np.nan)
    if new_cols:
        df_final_group = pd.concat([df_final_group, pd.DataFrame(new_cols, index=df_final_group.index)], axis=1)


    new_cols = {}
    for s_c, val, suff in series_value_config:
        result = _calculate_series_value_crossover(
            df_final_group.copy(), s_c, val, suff, local_logger
        )
        if result is None:
            continue
        kesisim_yukari, kesisim_asagi = result
        if len(kesisim_yukari) == len(df_final_group):
            new_cols[kesisim_yukari.name] = kesisim_yukari.values
        else:
            new_cols[kesisim_yukari.name] = np.full(len(df_final_group), np.nan)
        if len(kesisim_asagi) == len(df_final_group):
            new_cols[kesisim_asagi.name] = kesisim_asagi.values
        else:
            new_cols[kesisim_asagi.name] = np.full(len(df_final_group), np.nan)
    if new_cols:
        df_final_group = pd.concat([df_final_group, pd.DataFrame(new_cols, index=df_final_group.index)], axis=1)
    manual_last = {}
    if "bbm_20_2" in df_final_group.columns and "BBM_20_2" not in df_final_group.columns:
        manual_last["BBM_20_2"] = df_final_group["bbm_20_2"]
    if manual_last:
        df_final_group = pd.concat([df_final_group, pd.DataFrame(manual_last, index=df_final_group.index)], axis=1)
        
    return df_final_group


def hesapla_teknik_indikatorler_ve_kesisimler(df_islenmis_veri: pd.DataFrame, logger_param=None) -> pd.DataFrame | None:
    ana_logger = logger_param or logger
    ana_logger.info("Teknik indikatörler ve kesişim sinyalleri hesaplanmaya başlanıyor...")

    if df_islenmis_veri is None or df_islenmis_veri.empty:
        ana_logger.critical("İndikatör hesaplama için işlenmiş veri (df_islenmis_veri) boş veya None.")
        return None

    gerekli_sutunlar = ['tarih', 'open', 'high', 'low', 'close', 'volume', 'hisse_kodu']
    eksik_sutunlar = [col for col in gerekli_sutunlar if col not in df_islenmis_veri.columns]
    if eksik_sutunlar:
        ana_logger.critical(f"İndikatör hesaplama ana fonksiyonuna gelen DataFrame'de temel sütunlar eksik: {eksik_sutunlar}.")
        return None

    _ekle_psar(df_islenmis_veri)

    ta_strategy_params = config.TA_STRATEGY
    series_series_crossovers = config.SERIES_SERIES_CROSSOVERS
    series_value_crossovers = config.SERIES_VALUE_CROSSOVERS
    ozel_sutun_params = config.OZEL_SUTUN_PARAMS
    indikator_ad_eslestirme = config.INDIKATOR_AD_ESLESTIRME

    results_list = []
    grouped = df_islenmis_veri.groupby('hisse_kodu', group_keys=False)

    total_stocks = len(df_islenmis_veri['hisse_kodu'].unique())
    current_processed_count_main = 0

    for hisse_kodu, group_df_original in grouped: # group_df_original zaten 'tarih'e göre sıralı geliyor (preprocessor'dan)
        current_processed_count_main += 1
        # _calculate_group_indicators_and_crossovers fonksiyonuna RangeIndex'li ve 'tarih' sütunlu df gönderiyoruz.
        # Bu fonksiyon içinde DatetimeIndex'e çevrilip, sonra tekrar RangeIndex'e ve 'tarih' sütununa sahip olarak dönüyor.
        group_df_for_calc = group_df_original.reset_index(drop=True) # Her ihtimale karşı indeksi sıfırla

        if current_processed_count_main % 50 == 0 or current_processed_count_main == 1 or current_processed_count_main == total_stocks:
            ana_logger.info(f"({current_processed_count_main}/{total_stocks}) {hisse_kodu} için indikatör hesaplama...")

        calculated_group = _calculate_group_indicators_and_crossovers(
            hisse_kodu,
            group_df_for_calc, # RangeIndex'li df gönderiliyor
            ta_strategy_params,
            series_series_crossovers,
            series_value_crossovers,
            ozel_sutun_params,
            indikator_ad_eslestirme,
            ana_logger
        )
        if calculated_group is not None and not calculated_group.empty:
            results_list.append(calculated_group) # calculated_group zaten RangeIndex'li ve 'tarih' sütunlu dönmeli
        else:
            ana_logger.warning(f"{hisse_kodu} için indikatör hesaplama sonucu boş veya None döndü.")

    if not results_list:
        ana_logger.error("Hiçbir hisse için geçerli indikatör sonucu üretilemedi. Son DataFrame boş olacak.")
        return pd.DataFrame()

    try:
        df_sonuc = pd.concat(results_list, ignore_index=True) #ignore_index=True zaten RangeIndex oluşturur
        
        if 'tarih' in df_sonuc.columns and not pd.api.types.is_datetime64_any_dtype(df_sonuc['tarih']):
             df_sonuc['tarih'] = pd.to_datetime(df_sonuc['tarih'], errors='coerce')
        elif 'tarih' not in df_sonuc.columns:
             ana_logger.error("Birleştirilmiş sonuç DataFrame'inde 'tarih' sütunu bulunmuyor!")


        df_sonuc.sort_values(by=['hisse_kodu', 'tarih'], inplace=True, na_position='first')
        df_sonuc.reset_index(drop=True, inplace=True)

        ana_logger.info(f"Tüm {current_processed_count_main} hisse için indikatör ve kesişim hesaplamaları tamamlandı. Son DataFrame boyutu: {df_sonuc.shape}")
        if not df_sonuc.empty:
             ana_logger.info(f"Filtrelemeye gönderilecek DataFrame sütunları ({len(df_sonuc.columns)} adet): {df_sonuc.columns.tolist()}")
        return df_sonuc
    except Exception as e_concat:
        ana_logger.critical(f"Hesaplanan indikatörler birleştirilirken KRİTİK HATA: {e_concat}", exc_info=True)
        return pd.DataFrame()
