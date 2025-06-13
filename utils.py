# utils.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Yardımcı Fonksiyonlar (Örn: Kesişimler)
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Yorumlar eklendi, NaN yönetimi teyit edildi)

import pandas as pd
import logging

# Bu modül kendi logger'ını kullanır, logger_setup.py'den get_logger ile çağrılmazsa.
# Ancak genellikle diğer modüller tarafından import edildiği için, çağıran modülün logger'ı geçerli olur.
# Eğer bu dosya tek başına test edilirse diye temel bir logger ayarı.
try:
    from logger_setup import get_logger

    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.warning(
            "logger_setup.py bulunamadı, utils.py kendi temel logger'ını kullanıyor."
        )


def crosses_above(s1: pd.Series | None, s2: pd.Series | None) -> pd.Series:
    """s1 serisinin s2 serisini yukarı doğru kesip kesmediğini kontrol eder."""
    common_index = None
    if s1 is not None:
        common_index = s1.index
    elif s2 is not None:
        common_index = s2.index

    if s1 is None or s2 is None:
        return pd.Series(False, index=common_index, dtype=bool)

    try:
        nan_mask = s1.isna() | s2.isna()
        out = (s1.shift(1) < s2.shift(1)) & (s1 >= s2)
        out[nan_mask] = False
        out = out.astype(bool)
        if not out.index.equals(s1.index):
            out = out.reindex(s1.index, fill_value=False)
        return out
    except Exception as e:
        logger.error(f"crosses_above fonksiyonunda kritik hata: {e}", exc_info=False)
        return pd.Series(False, index=common_index, dtype=bool)


def crosses_below(s1: pd.Series | None, s2: pd.Series | None) -> pd.Series:
    """s1 serisinin s2'yi aşağı doğru kesip kesmediğini kontrol eder."""
    common_index = None
    if s1 is not None:
        common_index = s1.index
    elif s2 is not None:
        common_index = s2.index

    if s1 is None or s2 is None:
        return pd.Series(False, index=common_index, dtype=bool)

    try:
        nan_mask = s1.isna() | s2.isna()
        out = (s1.shift(1) > s2.shift(1)) & (s1 <= s2)
        out[nan_mask] = False
        out = out.astype(bool)
        if not out.index.equals(s1.index):
            out = out.reindex(s1.index, fill_value=False)
        return out
    except Exception as e:
        logger.error(f"crosses_below fonksiyonunda kritik hata: {e}", exc_info=False)
        return pd.Series(False, index=common_index, dtype=bool)


# safe_pct_change gibi diğer yardımcı fonksiyonlar buraya eklenebilir.
# Şimdilik sadece kesişimler var.


def extract_columns_from_filters(
    df_filters: pd.DataFrame | None,
    series_series: list | None,
    series_value: list | None,
) -> set:
    """Filtre sorgularında ve crossover tanımlarında geçen kolon adlarını döndürür."""
    try:
        from filter_engine import _extract_query_columns
    except Exception:
        # filter_engine import edilemezse boş set döndür
        return set()

    wanted = set()
    if (
        df_filters is not None
        and not df_filters.empty
        and "PythonQuery" in df_filters.columns
    ):
        for q in df_filters["PythonQuery"].dropna().astype(str):
            wanted |= _extract_query_columns(q)

    for entry in series_series or []:
        if len(entry) >= 2:
            wanted.add(entry[0])
            wanted.add(entry[1])

    for entry in series_value or []:
        if len(entry) >= 1:
            wanted.add(entry[0])

    return wanted
