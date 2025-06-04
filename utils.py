# utils.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Yardımcı Fonksiyonlar (Örn: Kesişimler)
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Yorumlar eklendi, NaN yönetimi teyit edildi)

import pandas as pd
import numpy as np
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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.warning("logger_setup.py bulunamadı, utils.py kendi temel logger'ını kullanıyor.")


def crosses_above(s1: pd.Series, s2: pd.Series) -> pd.Series:
    """
    s1 serisinin s2 serisini yukarı doğru kesip kesmediğini kontrol eder.
    (Önceki periyotta s1 < s2 iken, mevcut periyotta s1 > s2 olması durumu)

    Args:
        s1 (pd.Series): İlk seri.
        s2 (pd.Series): İkinci seri (veya s1 ile aynı indekse sahip skaler değer serisi).

    Returns:
        pd.Series: Kesişimin olduğu yerlerde True, diğerlerinde False içeren boolean Seri.
    """
    try:
        if not (isinstance(s1, pd.Series) and isinstance(s2, pd.Series)):
            logger.warning(f"crosses_above: Beklenmeyen tipte girdiler. s1: {type(s1)}, s2: {type(s2)}", exc_info=False)
            # Mümkünse s1'in index'iyle boş bir seri dön, değilse tamamen boş seri.
            idx = getattr(s1, 'index', getattr(s2, 'index', None))
            return pd.Series(False, index=idx, dtype=bool) if idx is not None else pd.Series(dtype=bool)

        if s1.empty or s2.empty or len(s1) < 2 or len(s2) < 2: # Kesişim için en az 2 periyot gerekir
            # logger.debug(f"crosses_above: Yetersiz veri. s1_len: {len(s1)}, s2_len: {len(s2)}")
            return pd.Series(False, index=s1.index, dtype=bool)

        # Bir önceki periyottaki değerler
        s1_prev = s1.shift(1)
        s2_prev = s2.shift(1)

        # Herhangi bir NaN varsa o satırda kesişim False olmalı
        nan_mask = pd.isna(s1) | pd.isna(s1_prev) | pd.isna(s2) | pd.isna(s2_prev)

        # Kesişim koşulu: Önceki periyotta s1 < s2 VE mevcut periyotta s1 > s2
        condition = (s1_prev < s2_prev) & (s1 > s2)

        result = pd.Series(condition, index=s1.index, dtype=bool)
        result[nan_mask] = False # NaN içeren satırlarda kesişim olmaz
        return result

    except Exception as e:
        s1_name = getattr(s1, 'name', 's1_unnamed')
        s2_name = getattr(s2, 'name', 's2_unnamed')
        logger.error(f"crosses_above fonksiyonunda ({s1_name} vs {s2_name}) kritik hata: {e}", exc_info=False)
        idx = getattr(s1, 'index', None)
        return pd.Series(False, index=idx, dtype=bool) if idx is not None else pd.Series(dtype=bool)


def crosses_below(s1: pd.Series, s2: pd.Series) -> pd.Series:
    """
    s1 serisinin s2 serisini aşağı doğru kesip kesmediğini kontrol eder.
    (Önceki periyotta s1 > s2 iken, mevcut periyotta s1 < s2 olması durumu)

    Args:
        s1 (pd.Series): İlk seri.
        s2 (pd.Series): İkinci seri (veya s1 ile aynı indekse sahip skaler değer serisi).

    Returns:
        pd.Series: Kesişimin olduğu yerlerde True, diğerlerinde False içeren boolean Seri.
    """
    try:
        if not (isinstance(s1, pd.Series) and isinstance(s2, pd.Series)):
            logger.warning(f"crosses_below: Beklenmeyen tipte girdiler. s1: {type(s1)}, s2: {type(s2)}", exc_info=False)
            idx = getattr(s1, 'index', getattr(s2, 'index', None))
            return pd.Series(False, index=idx, dtype=bool) if idx is not None else pd.Series(dtype=bool)

        if s1.empty or s2.empty or len(s1) < 2 or len(s2) < 2:
            # logger.debug(f"crosses_below: Yetersiz veri. s1_len: {len(s1)}, s2_len: {len(s2)}")
            return pd.Series(False, index=s1.index, dtype=bool)

        s1_prev = s1.shift(1)
        s2_prev = s2.shift(1)

        nan_mask = pd.isna(s1) | pd.isna(s1_prev) | pd.isna(s2) | pd.isna(s2_prev)

        # Kesişim koşulu: Önceki periyotta s1 > s2 VE mevcut periyotta s1 < s2
        condition = (s1_prev > s2_prev) & (s1 < s2)

        result = pd.Series(condition, index=s1.index, dtype=bool)
        result[nan_mask] = False
        return result

    except Exception as e:
        s1_name = getattr(s1, 'name', 's1_unnamed')
        s2_name = getattr(s2, 'name', 's2_unnamed')
        logger.error(f"crosses_below fonksiyonunda ({s1_name} vs {s2_name}) kritik hata: {e}", exc_info=False)
        idx = getattr(s1, 'index', None)
        return pd.Series(False, index=idx, dtype=bool) if idx is not None else pd.Series(dtype=bool)

# safe_pct_change gibi diğer yardımcı fonksiyonlar buraya eklenebilir.
# Şimdilik sadece kesişimler var.
