# indicator_calculator.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Teknik İndikatörler ve Kesişim Sinyalleri Hesaplama
# Tuğrul Karaaslan & Gemini
# Tarih: 19 Mayıs 2025 (Tüm özel fonksiyonlar eklendi, reset_index düzeltildi, filtre uyumu artırıldı v2)

import pandas as pd
import pandas_ta as ta
import numpy as np
import config
import utils

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

def _calculate_series_series_crossover(group_df: pd.DataFrame, s1_col: str, s2_col: str, col_name_above: str, col_name_below: str, logger_param=None) -> tuple[pd.Series, pd.Series]:
    local_logger = logger_param or logger
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    empty_above = pd.Series(False, index=group_df.index, name=col_name_above, dtype=bool)
    empty_below = pd.Series(False, index=group_df.index, name=col_name_below, dtype=bool)

    missing_cols = []
    if s1_col not in group_df.columns: missing_cols.append(s1_col)
    if s2_col not in group_df.columns: missing_cols.append(s2_col)

    if missing_cols:
        local_logger.debug(f"{hisse_str}: Kesişim ({s1_col} vs {s2_col}) için eksik sütun(lar): {', '.join(missing_cols)}")
        return empty_above, empty_below
    try:
        s1 = pd.to_numeric(group_df[s1_col], errors='coerce')
        s2 = pd.to_numeric(group_df[s2_col], errors='coerce')
        if s1.isnull().all() or s2.isnull().all():
            local_logger.debug(f"{hisse_str}: Kesişim ({s1_col} vs {s2_col}) için serilerden biri tamamen NaN.")
            return empty_above, empty_below
        kesisim_yukari = utils.crosses_above(s1, s2).rename(col_name_above)
        kesisim_asagi = utils.crosses_below(s1, s2).rename(col_name_below)
        return kesisim_yukari, kesisim_asagi
    except Exception as e:
        local_logger.error(f"{hisse_str}: _calculate_series_series_crossover ({s1_col} vs {s2_col}) hatası: {e}", exc_info=False)
        return empty_above, empty_below

def _calculate_series_value_crossover(group_df: pd.DataFrame, s_col: str, value: float, suffix: str, logger_param=None) -> tuple[pd.Series, pd.Series]:
    local_logger = logger_param or logger
    hisse_str = group_df['hisse_kodu'].iloc[0] if not group_df.empty and 'hisse_kodu' in group_df.columns else 'Bilinmeyen Hisse'
    col_name_above = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_yukari"
    col_name_below = f"{s_col}_keser_{str(suffix).replace('.', 'p')}_asagi"
    empty_above = pd.Series(False, index=group_df.index, name=col_name_above, dtype=bool)
    empty_below = pd.Series(False, index=group_df.index, name=col_name_below, dtype=bool)

    if s_col not in group_df.columns:
        local_logger.debug(f"{hisse_str}: Kesişim ({s_col} vs {value}) için eksik sütun: {s_col}")
        return empty_above, empty_below
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
    datetime_index_set_successfully = False
    if 'tarih' in group_df_dt_indexed.columns:
        if not pd.api.types.is_datetime64_any_dtype(group_df_dt_indexed['tarih']):
            group_df_dt_indexed['tarih'] = pd.to_datetime(group_df_dt_indexed['tarih'], errors='coerce')
        if not group_df_dt_indexed['tarih'].isnull().all():
            try:
                group_df_dt_indexed = group_df_dt_indexed.set_index(pd.DatetimeIndex(group_df_dt_indexed['tarih']), drop=True)
                datetime_index_set_successfully = True
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

    try:
        group_df_dt_indexed.ta.strategy(ta_strategy, timed=False, append=True)
    except Exception as e_ta:
        local_logger.error(f"{hisse_kodu}: pandas-ta stratejisi hatası: {e_ta}", exc_info=True)
        # Hata durumunda, o ana kadar eklenen sütunlarla RangeIndex'li orijinal df'i birleştirmeye çalış
        # Bu kısım karmaşıklaşabilir, en iyisi temel df'i döndürmek.
        return group_df_input[['hisse_kodu', 'tarih'] + [c for c in required_ohlcv if c in group_df_input.columns]].drop_duplicates()

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
    new_ta_cols = [col for col in group_df_dt_indexed.columns if col not in group_df_input.columns and col not in required_ohlcv]
    for col in new_ta_cols:
        if len(group_df_dt_indexed[col].values) == len(df_final_group):
             df_final_group[col] = group_df_dt_indexed[col].values
        else:
            local_logger.warning(f"{hisse_kodu}: pandas-ta sütunu '{col}' kopyalanırken boyut uyuşmazlığı. Atlanıyor.")


    # Özel Sütunlar (df_final_group üzerinde, zaten RangeIndex'li)
    for sutun_conf in ozel_sutun_conf:
        yeni_sutun_adi = sutun_conf['name']
        fonksiyon_adi_str = sutun_conf['function']
        parametreler = sutun_conf.get('params', {})
        try:
            fonksiyon = globals().get(fonksiyon_adi_str)
            if fonksiyon:
                result_series = fonksiyon(df_final_group.copy(), **parametreler) # Fonksiyona kopya ver
                if result_series is not None and len(result_series) == len(df_final_group):
                    df_final_group[yeni_sutun_adi] = result_series.values # .values ile atama
                # ... (NaN ve boyut kontrolü) ...
            else: # ... (hata logu) ...
                 df_final_group[yeni_sutun_adi] = np.nan
                 local_logger.error(f"{hisse_kodu}: Özel sütun için '{fonksiyon_adi_str}' fonksiyonu bulunamadı.")
        except Exception as e_ozel: # ... (hata logu) ...
             df_final_group[yeni_sutun_adi] = np.nan
             local_logger.error(f"{hisse_kodu}: Özel sütun '{yeni_sutun_adi}' hesaplanırken hata: {e_ozel}", exc_info=False)


    # Kesişimler (df_final_group üzerinde)
    for s1_c, s2_c, c_above, c_below in series_series_config:
        kesisim_yukari, kesisim_asagi = _calculate_series_series_crossover(df_final_group.copy(), s1_c, s2_c, c_above, c_below, local_logger)
        if len(kesisim_yukari) == len(df_final_group): df_final_group[c_above] = kesisim_yukari.values
        else: df_final_group[c_above] = np.nan
        if len(kesisim_asagi) == len(df_final_group): df_final_group[c_below] = kesisim_asagi.values
        else: df_final_group[c_below] = np.nan


    for s_c, val, suff in series_value_config:
        kesisim_yukari, kesisim_asagi = _calculate_series_value_crossover(df_final_group.copy(), s_c, val, suff, local_logger)
        if len(kesisim_yukari) == len(df_final_group): df_final_group[kesisim_yukari.name] = kesisim_yukari.values
        else: df_final_group[kesisim_yukari.name] = np.nan
        if len(kesisim_asagi) == len(df_final_group): df_final_group[kesisim_asagi.name] = kesisim_asagi.values
        else: df_final_group[kesisim_asagi.name] = np.nan
        
    return df_final_group
    # Güvenlik kontrolü: İndikatörler df'de var mı?
    assert all([k in df.columns for k in df.columns if k.startswith(('RSI', 'MACD', 'EMA', 'BOLL'))]), 'Bazı indikatör sütunları eksik!'


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
