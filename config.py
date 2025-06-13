# config.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Yapılandırma Dosyası
# Tuğrul Karaaslan & Gemini
# Tarih: 19 Mayıs 2025 (Ichimoku ve Aroon ad eşleştirmeleri filtre uyumu için SON DÜZELTMELER)

import os
import logging
import numpy as np

# pandas_ta bazı ortamlarda numpy.NaN sabitini kullanarak yükleniyor.
# NumPy 2.x sürümlerinde bu sabit olmadığı için import hatası
# yaşanmaması için eksikse tanımlama yapıyoruz.
if not hasattr(np, "NaN"):
    np.NaN = np.nan

import pandas_ta as ta
import sys

# Temel Dizinler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CIKTI_KLASORU = os.path.join(BASE_DIR, 'cikti')
VERI_KLASORU = os.path.join(BASE_DIR, 'veri')
HISSE_DOSYA_PATTERN = os.path.join(VERI_KLASORU, '*.csv')
FILTRE_DOSYA_YOLU = os.path.join(VERI_KLASORU, '15.csv')
PARQUET_ANA_DOSYA_YOLU = os.path.join(VERI_KLASORU, 'birlesik_hisse_verileri.parquet')
LOG_DOSYA_YOLU = os.path.join(BASE_DIR, 'finansal_analiz_sistemi.log')
CSV_OZET_DOSYA_ADI = 'backtest_ozet_raporu.csv'

FILTRE_SUTUN_ADLARI_MAP = {
    'FilterCode': 'FilterCode',
    'PythonQuery': 'PythonQuery'
}

TARAMA_TARIHI_DEFAULT = "07.03.2025"
SATIS_TARIHI_DEFAULT = "10.03.2025"
TIMEZONE = "Europe/Istanbul"
TR_HOLIDAYS_REMOVE = True

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(process)d - %(threadName)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

IS_COLAB = 'google.colab' in sys.modules

OHLCV_MAP = {
    'Tarih': 'tarih', 'Açılış': 'open', 'Yüksek': 'high', 'Düşük': 'low',
    'Kapanış': 'close', 'Miktar': 'volume', 'Hacim': 'volume_tl',
    'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'CLOSE': 'close', 'VOLUME': 'volume',
    'ACILIS': 'open', 'YUKSEK': 'high', 'DUSUK': 'low', 'KAPANIS': 'close', 'HACIM': 'volume',
    'hacim_lot': 'volume',
}

TA_STRATEGY = ta.Strategy(
    name="Comprehensive Strategy for Filters - All Active v3",
    description="Filtrelerle tam uyumlu olması hedeflenen tüm indikatörler aktif, ad eşleştirmeleri son revize.",
    ta=[
        {"kind": "atr", "length": 14, "col_names": ("atr_14",)},
        {"kind": "bbands", "length": 20, "std": 2, "col_names": ("bbl_20_2", "bbm_20_2", "bbu_20_2", "bbb_20_2", "bbp_20_2")},
        {"kind": "donchian", "lower_length": 20, "upper_length": 20, "col_names": ("dcl_20_20", "dcm_20_20", "dcu_20_20")},
        {"kind": "kc", "length": 20, "scalar": 2, "col_names": ("kcl_20_2", "kcm_20_2", "kcu_20_2")},
        {"kind": "rsi", "length": 14, "col_names": ("rsi_14",)},
        {"kind": "rsi", "length": 7, "col_names": ("rsi_7",)},
        {"kind": "apo", "fast": 12, "slow": 26, "col_names": ("apo_12_26",)},
        {"kind": "macd", "fast": 12, "slow": 26, "signal": 9, "col_names": ("macd_line", "macd_signal", "macd_hist")},
        {"kind": "stoch", "k": 14, "d": 3, "smooth_k": 3, "col_names": ("stoch_k", "stoch_d")},
        {"kind": "stochrsi", "length": 14, "rsi_length": 14, "k": 3, "d": 3, "col_names": ("stochrsi_k", "stochrsi_d")},
        {"kind": "willr", "length": 14, "col_names": ("williamspercentr_14",)},
        {"kind": "cci", "length": 20, "col_names": ("cci_20",)},
        {"kind": "cmo", "length": 14, "col_names": ("cmo_14",)},
        {"kind": "roc", "length": 12, "col_names": ("roc_12",)},
        {"kind": "mom", "length": 10, "col_names": ("mom_10",)},
        {"kind": "ppo", "fast": 12, "slow": 26, "signal": 9, "col_names": ("ppo_line", "ppo_signal", "ppo_hist")},
        {"kind": "sma", "length": 5, "col_names": ("sma_5",)},
        {"kind": "sma", "length": 10, "col_names": ("sma_10",)},
        {"kind": "sma", "length": 20, "col_names": ("sma_20",)},
        {"kind": "sma", "length": 21, "col_names": ("sma_21",)},
        {"kind": "sma", "length": 30, "col_names": ("sma_30",)},
        {"kind": "sma", "length": 50, "col_names": ("sma_50",)},
        {"kind": "sma", "length": 100, "col_names": ("sma_100",)},
        {"kind": "sma", "length": 200, "col_names": ("sma_200",)},
        {"kind": "ema", "length": 5, "col_names": ("ema_5",)},
        {"kind": "ema", "length": 8, "col_names": ("ema_8",)},
        {"kind": "ema", "length": 10, "col_names": ("ema_10",)},
        {"kind": "ema", "length": 13, "col_names": ("ema_13",)},
        {"kind": "ema", "length": 20, "col_names": ("ema_20",)},
        {"kind": "ema", "length": 21, "col_names": ("ema_21",)},
        {"kind": "ema", "length": 30, "col_names": ("ema_30",)},
        {"kind": "ema", "length": 50, "col_names": ("ema_50",)},
        {"kind": "ema", "length": 100, "col_names": ("ema_100",)},
        {"kind": "ema", "length": 200, "col_names": ("ema_200",)},
        {"kind": "dema", "length": 20, "col_names": ("dema_20",)},
        {"kind": "tema", "length": 20, "col_names": ("tema_20",)},
        {"kind": "wma", "length": 20, "col_names": ("wma_20",)},
        {"kind": "hma", "length": 9, "col_names": ("hma_9",)},
        {"kind": "vwma", "length": 20, "col_names": ("vwma_20",)},
        {"kind": "adx", "length": 14, "col_names": ("adx_14", "DMP_14", "DMN_14")},
        {"kind": "ichimoku", "tenkan": 9, "kijun": 26, "senkou": 52, "include_chikou": True, "col_names": ("ITS_9", "IKS_26", "ISA_9_26_52", "ISB_26_52", "ICS_26")},
        {"kind": "psar", "col_names": ("psar_long", "psar_short", "psar_af", "psar_reversal")},
        {"kind": "supertrend", "length": 7, "multiplier": 3, "col_names": ("supertrend_direction_7_3", "supertrend_7_3", "supertrend_long_7_3", "supertrend_short_7_3")}, # Düzeltildi
        {"kind": "vortex", "length": 14, "col_names": ("vortex_pos", "vortex_neg")},
        {"kind": "aroon", "length": 14, "col_names": ("AROOND_14", "AROONU_14", "AROONOSC_14")},
        {"kind": "obv", "col_names": ("obv",)},
        {"kind": "cmf", "length": 20, "col_names": ("cmf_20",)},
        {"kind": "mfi", "length": 14, "col_names": ("mfi_14",)},
        {"kind": "vwap", "col_names": ("vwap",)},
        {"kind": "efi", "length": 13, "col_names": ("efi_13",)},
        {"kind": "ad", "col_names": ("ad_line",)},
        {"kind": "adosc", "fast": 3, "slow": 10, "col_names": ("adosc_3_10",)},
    ]
)

INDIKATOR_AD_ESLESTIRME = {
    'bbl_20_2.0': 'bbl_20_2', 'bbm_20_2.0': 'bbm_20_2', 'bbu_20_2.0': 'bbu_20_2',
    'bbb_20_2.0': 'bbb_20_2', 'bbp_20_2.0': 'bbp_20_2',
    'kcl_20_2.0': 'kcl_20_2', 'kcm_20_2.0': 'kcm_20_2', 'kcu_20_2.0': 'kcu_20_2',
    'macdh_12_26_9': 'macd_hist', 'macds_12_26_9': 'macd_signal', 'macd_12_26_9': 'macd_line',
    'stochk_14_3_3': 'stoch_k', 'stochd_14_3_3': 'stoch_d',
    'stochrsi_k_14_14_3_3': 'stochrsi_k', 'stochrsi_d_14_14_3_3': 'stochrsi_d',
    'cci_20_0.015': 'cci_20',
    'ppoh_12_26_9': 'ppo_hist', 'ppos_12_26_9': 'ppo_signal', 'ppo_12_26_9': 'ppo_line',
    'psarl_0.02_0.2': 'psar_long', 'psars_0.02_0.2': 'psar_short',
    'psaraf_0.02_0.2': 'psar_af', 'psarr_0.02_0.2': 'psar_reversal',
    'supertd_7_3.0': 'supertrend_direction_7_3', 
    'supert_7_3.0': 'supertrend_7_3',
    # pandas-ta kolonu 'supertrend_long_7_3' olarak üretildiğinden
    # eşleştirme hedefi de bu isimle yapılmalı
    'supertl_7_3.0': 'supertrend_long_7_3',
    'superts_7_3.0': 'supertrend_short_7_3',
    'vwap_d': 'vwap',
    'dmp_14': 'positivedirectionalindicator_14',
    'dmn_14': 'negativedirectionalindicator_14',
    'aroonu_14': 'aroonu_14',
    'aroond_14': 'aroond_14',
    'aroonosc_14': 'AROONOSC_14', # Filtrede büyük harf arandığı için düzeltildi
    'mom_10': 'momentum_10',
    # Ichimoku: pandas-ta'nın ürettiği (TA_STRATEGY'deki col_names) -> Filtrelerde aranan/beklenen adlar
    'its_9': 'ichimoku_conversionline',
    'iks_26': 'ichimoku_baseline',
    'isa_9_26_52': 'ichimoku_leadingspana', # Düzeltildi (filtredeki ad)
    'isb_26_52': 'ichimoku_leadingspanb',   # Düzeltildi (filtredeki ad)
    'ics_26': 'ichimoku_lagging_span'
}

OZEL_SUTUN_PARAMS = [
    {'name': 'relative_volume', 'function': '_calculate_relative_volume', 'params': {'window': 20, 'col_name_prefix': 'volume'}},
    {'name': 'volume_price', 'function': '_calculate_volume_price', 'params': {'col_name_prefix_vol': 'volume', 'col_name_prefix_price': 'close'}},
    {'name': 'change_from_open_percent', 'function': '_calculate_change_from_open', 'params': {'col_name_open': 'open', 'col_name_close': 'close'}},
    {'name': 'percentage_from_ath', 'function': '_calculate_percentage_from_all_time_high', 'params': {'price_col': 'high'}},
    {'name': 'change_1w_percent', 'function': '_calculate_change_percent', 'params': {'period': 5, 'price_col': 'close', 'output_col_name': 'change_1w_percent'}},
    {'name': 'change_1m_percent', 'function': '_calculate_change_percent', 'params': {'period': 20, 'price_col': 'close', 'output_col_name': 'change_1m_percent'}},
    {'name': 'change_1h_percent', 'function': '_calculate_change_percent', 'params': {'period': 1, 'price_col': 'close', 'output_col_name': 'change_1h_percent'}},
    {'name': 'volume_20_sma', 'function': '_calculate_sma', 'params': {'period': 20, 'data_col': 'volume'}},
    {'name': 'prev_high_1', 'function': '_get_previous_bar_value', 'params': {'data_col': 'high', 'shift_by': 1}},
    {'name': 'prev_low_1', 'function': '_get_previous_bar_value', 'params': {'data_col': 'low', 'shift_by': 1}},
    {'name': 'psar', 'function': '_calculate_combined_psar', 'params': {}},
    {'name': 'percentage_from_52w_high', 'function': '_calculate_percentage_from_period_high_low', 'params': {'price_col': 'high', 'period': 252, 'mode': 'high'}},
    {'name': 'percentage_from_52w_low', 'function': '_calculate_percentage_from_period_high_low', 'params': {'price_col': 'low', 'period': 252, 'mode': 'low'}},
    {'name': 'volume_change_percent_1d', 'function': '_calculate_change_percent', 'params': {'period': 1, 'price_col': 'volume', 'output_col_name': 'volume_change_percent_1d'}},
    {'name': 'classicpivots_1h_p', 'function': '_calculate_classicpivots_1h_p', 'params': {}},
]

SERIES_SERIES_CROSSOVERS = [
    ('sma_5', 'sma_10', 'sma_5_keser_sma_10_yukari', 'sma_5_keser_sma_10_asagi'),
    ('sma_10', 'sma_20', 'sma_10_keser_sma_20_yukari', 'sma_10_keser_sma_20_asagi'),
    ('sma_20', 'sma_50', 'sma_20_keser_sma_50_yukari', 'sma_20_keser_sma_50_asagi'),
    ('sma_10', 'sma_50', 'sma_10_keser_sma_50_yukari', 'sma_10_keser_sma_50_asagi'),
    ('sma_50', 'sma_100', 'sma_50_keser_sma_100_yukari', 'sma_50_keser_sma_100_asagi'),
    ('sma_50', 'sma_200', 'sma_50_keser_sma_200_yukari', 'sma_50_keser_sma_200_asagi'),
    ('ema_5', 'ema_10', 'ema_5_keser_ema_10_yukari', 'ema_5_keser_ema_10_asagi'),
    ('ema_10', 'ema_20', 'ema_10_keser_ema_20_yukari', 'ema_10_keser_ema_20_asagi'),
    ('ema_20', 'ema_50', 'ema_20_keser_ema_50_yukari', 'ema_20_keser_ema_50_asagi'),
    ('ema_50', 'ema_100', 'ema_50_keser_ema_100_yukari', 'ema_50_keser_ema_100_asagi'),
    ('ema_50', 'ema_200', 'ema_50_keser_ema_200_yukari', 'ema_50_keser_ema_200_asagi'),
    ('sma_5', 'sma_20', 'sma_5_keser_sma_20_yukari', 'sma_5_keser_sma_20_asagi'),
    ('close', 'sma_20', 'close_keser_sma_20_yukari', 'close_keser_sma_20_asagi'),
    ('close', 'sma_50', 'close_keser_sma_50_yukari', 'close_keser_sma_50_asagi'),
    ('close', 'sma_100', 'close_keser_sma_100_yukari', 'close_keser_sma_100_asagi'),
    ('close', 'sma_200', 'close_keser_sma_200_yukari', 'close_keser_sma_200_asagi'),
    ('macd_line', 'macd_signal', 'macd_line_keser_macd_signal_yukari', 'macd_line_keser_macd_signal_asagi'),
    ('ichimoku_conversionline', 'ichimoku_baseline', 'ichimoku_conversionline_keser_ichimoku_baseline_yukari', 'ichimoku_conversionline_keser_ichimoku_baseline_asagi'),
    ('close', 'ichimoku_baseline', 'close_keser_ichimoku_baseline_yukari', 'close_keser_ichimoku_baseline_asagi'),
    ('sma_30', 'close', 'sma_30_keser_close_asagi', 'sma_30_keser_close_yukari'),
    ('sma_5', 'close', 'sma_5_keser_close_asagi', 'sma_5_keser_close_yukari'),
    ('close', 'bbu_20_2', 'close_keser_bbu_20_2_yukari', 'close_keser_bbu_20_2_asagi'),
    ('close', 'sma_21', 'close_keser_sma_21_yukari', 'close_keser_sma_21_asagi'),
    ('close', 'ema_21', 'close_keser_ema_21_yukari', 'close_keser_ema_21_asagi'),
    ('close', 'bbm_20_2', 'close_keser_bbm_20_2_yukari', 'close_keser_bbm_20_2_asagi'),
    ('close', 'classicpivots_1h_p', 'close_keser_classicpivots_1h_p_yukari', 'close_keser_classicpivots_1h_p_asagi'),
    ('close', 'ema_5', 'close_keser_ema_5_yukari', 'close_keser_ema_5_asagi'),
    ('close', 'ema_10', 'close_keser_ema_10_yukari', 'close_keser_ema_10_asagi'),
    ('ema_50', 'close', 'ema_50_keser_close_yukari', 'ema_50_keser_close_asagi'),
    ('sma_50', 'close', 'sma_50_keser_close_yukari', 'sma_50_keser_close_asagi'),
    ('sma_100', 'close', 'sma_100_keser_close_yukari', 'sma_100_keser_close_asagi'),
    ('sma_200', 'close', 'sma_200_keser_close_yukari', 'sma_200_keser_close_asagi'),
    ('positivedirectionalindicator_14', 'negativedirectionalindicator_14', 'positivedirectionalindicator_14_keser_negativedirectionalindicator_14_yukari', 'positivedirectionalindicator_14_keser_negativedirectionalindicator_14_asagi'),
    ('stoch_k', 'stoch_d', 'stoch_k_keser_stoch_d_yukari', 'stoch_k_keser_stoch_d_asagi'),
    ('stochrsi_d', 'stochrsi_k', 'stochrsi_d_keser_stochrsi_k_yukari', 'stochrsi_d_keser_stochrsi_k_asagi'),
    ('stochrsi_k', 'stochrsi_d', 'stochrsi_k_keser_stochrsi_d_yukari', 'stochrsi_k_keser_stochrsi_d_asagi'),
    ('ichimoku_leadingspana', 'ichimoku_leadingspanb', 'senkou_a_keser_senkou_b_yukari', 'senkou_a_keser_senkou_b_asagi'),
    ('close', 'psar', 'close_keser_psar_yukari', 'close_keser_psar_asagi'),
    ('psar', 'close', 'psar_keser_close_yukari', 'psar_keser_close_asagi'),
    ('close', 'supertrend_7_3', 'close_keser_supertrend_yukari', 'close_keser_supertrend_asagi'),
    ('hma_9', 'close', 'hma_9_keser_close_yukari', 'hma_9_keser_close_asagi'),
    ('hma_9', 'sma_20', 'hma_9_keser_sma_20_yukari', 'hma_9_keser_sma_20_asagi'),
    ('vwma_20', 'close', 'vwma_20_keser_close_yukari', 'vwma_20_keser_close_asagi'),
    ('rsi_7', 'rsi_14', 'rsi_7_keser_rsi_14_yukari', 'rsi_7_keser_rsi_14_asagi'),
    ('close', 'dcm_20_20', 'close_keser_dcm_20_20_yukari', 'close_keser_dcm_20_20_asagi'),
    ('macd_signal', 'macd_line', 'macd_signal_keser_macd_line_yukari', 'macd_signal_keser_macd_line_asagi'),
    ('ema_5', 'ema_20', 'ema_5_keser_ema_20_yukari', 'ema_5_keser_ema_20_asagi'),
    ('ema_5', 'ema_50', 'ema_5_keser_ema_50_yukari', 'ema_5_keser_ema_50_asagi'),
    ('ema_5', 'close', 'ema_5_keser_close_yukari', 'ema_5_keser_close_asagi'),
    ('ema_10', 'close', 'ema_10_keser_close_yukari', 'ema_10_keser_close_asagi'),
    ('ema_20', 'close', 'ema_20_keser_close_yukari', 'ema_20_keser_close_asagi'),
    ('ema_100', 'close', 'ema_100_keser_close_yukari', 'ema_100_keser_close_asagi'),
    ('ema_200', 'close', 'ema_200_keser_close_yukari', 'ema_200_keser_close_asagi'),
    ('close', 'ema_100', 'close_keser_ema_100_yukari', 'close_keser_ema_100_asagi'),
    ('close', 'ema_200', 'close_keser_ema_200_yukari', 'close_keser_ema_200_asagi'),
    ('close', 'ema_8', 'close_keser_ema_8_yukari', 'close_keser_ema_8_asagi'),
    ('close', 'ema_13', 'close_keser_ema_13_yukari', 'close_keser_ema_13_asagi'),
    ('close', 'hma_9', 'close_keser_hma_9_yukari', 'close_keser_hma_9_asagi'),
    ('sma_5', 'close', 'sma_5_keser_close_yukari', 'sma_5_keser_close_asagi'),
    ('sma_10', 'close', 'sma_10_keser_close_yukari', 'sma_10_keser_close_asagi'),
    ('sma_20', 'close', 'sma_20_keser_close_yukari', 'sma_20_keser_close_asagi'),
    ('stoch_d', 'stoch_k', 'stoch_d_keser_stoch_k_yukari', 'stoch_d_keser_stoch_k_asagi'),
    ('ema_30', 'close', 'ema_30_keser_close_yukari', 'ema_30_keser_close_asagi'),
    ('close', 'ichimoku_conversionline', 'close_keser_ichimoku_conversionline_yukari', 'close_keser_ichimoku_conversionline_asagi'),
    ('ichimoku_conversionline', 'close', 'ichimoku_conversionline_keser_close_yukari', 'ichimoku_conversionline_keser_close_asagi'),
]

SERIES_VALUE_CROSSOVERS = [
    ('rsi_14', 50.0, '50p0'), ('rsi_14', 65.0, '65p0'), ('rsi_14', 30.0, '30p0'), ('rsi_14', 70.0, '70p0'), ('rsi_14', 20.0, '20p0'), ('rsi_14', 80.0, '80p0'), ('rsi_14', 40.0, '40p0'), ('rsi_14', 55.0, '55p0'), ('rsi_14', 60.0, '60p0'), ('rsi_14', 45.0, '45p0'), ('rsi_14', 35.0, '35p0'), ('rsi_14', 25.0, '25p0'), ('rsi_14', 75.0, '75p0'),
    ('rsi_7', 50.0, '50p0'), ('rsi_7', 70.0, '70p0'), ('rsi_7', 30.0, '30p0'),
    ('adx_14', 20.0, '20p0'), ('adx_14', 25.0, '25p0'), ('adx_14', 30.0, '30p0'),
    ('williamspercentr_14', -80.0, 'eksi80p0'), ('williamspercentr_14', -50.0, 'eksi50p0'), ('williamspercentr_14', -20.0, 'eksi20p0'),
    ('macd_line', 0.0, '0p0'),
    ('stoch_k', 20.0, '20p0'), ('stoch_k', 80.0, '80p0'),
    ('stoch_d', 20.0, '20p0'), ('stoch_d', 80.0, '80p0'),
    ('stochrsi_k', 20.0, '20p0'), ('stochrsi_k', 80.0, '80p0'),
    ('stochrsi_d', 20.0, '20p0'), ('stochrsi_d', 80.0, '80p0'),
    ('cmf_20', 0.0, '0p0'), ('cmf_20', 0.2, '0p2'), ('cmf_20', -0.2, 'eksi0p2'),
    ('cci_20', 100.0, '100p0'), ('cci_20', -100.0, 'eksi100p0'), ('cci_20', 0.0, '0p0'),
    ('momentum_10', 0.0, '0p0'), ('momentum_10', 1.0, '1p0'),
    ('mfi_14', 20.0, '20p0'), ('mfi_14', 80.0, '80p0'), ('mfi_14', 50.0, '50p0'),
    ('AROONOSC_14', 0.0, '0p0'), # Büyük harfle eşleşecek
    ('ppo_line', 0.0, '0p0')
]

ALIM_ZAMANI = "close"
SATIS_ZAMANI = "close"
KOMISYON_ORANI = 0.001

# Varsayılan backtest strateji adı. Değiştirilebilir.
UYGULANAN_STRATEJI = "basit_backtest"
