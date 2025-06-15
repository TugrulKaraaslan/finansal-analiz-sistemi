# report_utils.py
import pandas as pd
from pathlib import Path
import report_stats

# Default column orders for generated reports
DEFAULT_OZET_COLS = [
    "filtre_kodu",
    "hisse_sayisi",
    "ort_getiri_%",
    "en_yuksek_%",
    "en_dusuk_%",
    "islemli",
    "sebep_kodu",
    "sebep_aciklama",
    "tarama_tarihi",
    "satis_tarihi",
]

DEFAULT_DETAY_COLS = [
    "filtre_kodu",
    "hisse_kodu",
    "getiri_%",
    "basari",
    "strateji",
    "sebep_kodu",
]

DEFAULT_STATS_COLS = [
    "toplam_filtre",
    "islemli",
    "işlemsiz",
    "hatalı",
    "genel_başarı_%",
    "genel_ortalama_%",
]


def build_ozet_df(summary_df: pd.DataFrame, detail_df: pd.DataFrame, tarama_tarihi: str = "", satis_tarihi: str = "") -> pd.DataFrame:
    df = report_stats.build_ozet_df(summary_df, detail_df, tarama_tarihi, satis_tarihi)
    return df.reindex(columns=DEFAULT_OZET_COLS)


def build_detay_df(summary_df: pd.DataFrame, detail_df: pd.DataFrame, strateji: str | None = None) -> pd.DataFrame:
    df = report_stats.build_detay_df(summary_df, detail_df, strateji)
    return df.reindex(columns=DEFAULT_DETAY_COLS)


def build_stats_df(ozet_df: pd.DataFrame) -> pd.DataFrame:
    df = report_stats.build_stats_df(ozet_df)
    return df.reindex(columns=DEFAULT_STATS_COLS)


def plot_summary_stats(ozet_df: pd.DataFrame, detail_df: pd.DataFrame, std_threshold: float = 5.0):
    return report_stats.plot_summary_stats(ozet_df, detail_df, std_threshold)
