"""Lightweight helpers for running simplified backtests.

The module exposes minimal functions used by the CLI and tests to
simulate trades based on filter results.
"""

import numpy as np
import pandas as pd

from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.logging_config import get_logger

logger = get_logger(__name__)


def calistir_basit_backtest(
    filtre_sonuc_dict: dict,
    df_tum_veri: pd.DataFrame,
    satis_tarihi_str: str,
    tarama_tarihi_str: str,
    logger_param=None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run a simple backtest using the given filter results.

    Args:
        filtre_sonuc_dict (dict): Mapping of filter codes to selected stocks.
        df_tum_veri (pd.DataFrame): Full price dataset containing all tickers.
        satis_tarihi_str (str): Sale date in ``dd.mm.yyyy`` format.
        tarama_tarihi_str (str): Screening date in ``dd.mm.yyyy`` format.
        logger_param (logging.Logger, optional): Logger instance for status
            messages.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of summary and detail
        DataFrames.
    """
    if logger_param is None:
        logger_param = logger
    fn_logger = logger_param
    fn_logger.info(
        f"Basit backtest çalıştırılıyor. Tarama: {tarama_tarihi_str}, Satış: {satis_tarihi_str}"
    )

    if df_tum_veri is None or df_tum_veri.empty:
        fn_logger.error(
            "Backtest için ana veri (df_tum_veri) boş veya None. İşlem durduruluyor."
        )
        return pd.DataFrame(), pd.DataFrame()

    try:
        satis_tarihi = pd.to_datetime(satis_tarihi_str, format="%d.%m.%Y")
        tarama_tarihi = pd.to_datetime(tarama_tarihi_str, format="%d.%m.%Y")
    except ValueError:
        fn_logger.critical(
            f"Satış tarihi '{satis_tarihi_str}' veya tarama tarihi '{tarama_tarihi_str}' "
            "geçerli bir formatta (dd.mm.yyyy) değil. Backtest durduruluyor."
        )
        return pd.DataFrame(), pd.DataFrame()

    # Retrieve buy/sell timing configuration and commission
    alim_fiyat_sutunu = config.ALIM_ZAMANI  # e.g. "open"
    satis_fiyat_sutunu = config.SATIS_ZAMANI  # e.g. "open" or "close"
    komisyon_orani = config.KOMISYON_ORANI
    # Fallback: use ``close`` when the ``open`` column is missing
    if alim_fiyat_sutunu not in df_tum_veri.columns:
        alim_fiyat_sutunu = "close"
    if satis_fiyat_sutunu not in df_tum_veri.columns:
        satis_fiyat_sutunu = "close"
    # Record the strategy type for downstream reporting
    config.UYGULANAN_STRATEJI = "basit_backtest"

    summary_records = []
    detail_records = []

    for filtre_kodu, filtre_sonuc in filtre_sonuc_dict.items():
        hisse_kodlari = filtre_sonuc.get("hisseler", [])
        sebep = filtre_sonuc.get("sebep", "")

        hisse_getirileri = []
        for kod in hisse_kodlari:
            df_hisse = df_tum_veri[df_tum_veri["hisse_kodu"] == kod]
            alis = _get_fiyat(df_hisse, tarama_tarihi, alim_fiyat_sutunu, fn_logger)
            satis = _get_fiyat(df_hisse, satis_tarihi, satis_fiyat_sutunu, fn_logger)
            if pd.notna(alis) and pd.notna(satis):
                getiri = (satis / alis - 1 - komisyon_orani) * 100
            else:
                getiri = np.nan
            basari = "BAŞARILI" if pd.notna(getiri) and getiri > 0 else "BAŞARISIZ"
            detail_records.append(
                {
                    "filtre_kodu": filtre_kodu,
                    "hisse_kodu": kod,
                    "getiri_yuzde": round(getiri, 2) if pd.notna(getiri) else np.nan,
                    "basari": basari,
                }
            )
            hisse_getirileri.append(getiri)

        getiriler_seri = pd.Series(hisse_getirileri, dtype=float).dropna()
        ortalama = getiriler_seri.mean() if not getiriler_seri.empty else np.nan
        sebep_kodu = sebep
        if sebep == "OK" and getiriler_seri.empty:
            sebep_kodu = "DATA_GAP"

        summary_records.append(
            {
                "filtre_kodu": filtre_kodu,
                "ort_getiri_%": round(ortalama, 2) if pd.notna(ortalama) else np.nan,
                "sebep_kodu": sebep_kodu,
            }
        )

    rapor_df = pd.DataFrame(summary_records).sort_values("filtre_kodu")
    detay_df = pd.DataFrame(detail_records)

    return rapor_df, detay_df


def _get_fiyat(
    df_hisse_veri: pd.DataFrame,
    tarih: pd.Timestamp,
    zaman_sutun_adi: str,
    logger_param=None,
) -> float:
    """Return the price for ``tarih`` using the given column.

    Falls back to the nearest available date when an exact match is missing.

    Args:
        df_hisse_veri (pd.DataFrame): Stock data for a single ticker.
        tarih (pd.Timestamp): Date of interest.
        zaman_sutun_adi (str): Column name holding the desired price.
        logger_param (logging.Logger, optional): Logger instance for debug
            output.

    Returns:
        float: Price as ``float`` or ``NaN`` when unavailable.
    """
    if logger_param is None:
        logger_param = logger
    log = logger_param
    hisse_kodu_log = (
        df_hisse_veri["hisse_kodu"].iloc[0]
        if not df_hisse_veri.empty and "hisse_kodu" in df_hisse_veri.columns
        else "Bilinmeyen Hisse"
    )

    try:
        # Ensure the date column is of datetime type. The preprocessor should
        # normally handle this conversion.
        if not pd.api.types.is_datetime64_any_dtype(df_hisse_veri["tarih"]):
            df_hisse_veri["tarih"] = pd.to_datetime(
                df_hisse_veri["tarih"],
                dayfirst=True,
                errors="coerce",
            )

        veri_satiri = df_hisse_veri[df_hisse_veri["tarih"] == tarih]
        if veri_satiri.empty:
            sonraki = df_hisse_veri[df_hisse_veri["tarih"] > tarih]
            if not sonraki.empty:
                tarih2 = sonraki["tarih"].min()
            else:
                onceki = df_hisse_veri[df_hisse_veri["tarih"] < tarih]
                tarih2 = onceki["tarih"].max() if not onceki.empty else None

            if tarih2 is not None:
                log.info(
                    f"{hisse_kodu_log} için {tarih.strftime('%d.%m.%Y')} tarihli fiyat bulunamadı. "
                    f"{tarih2.strftime('%d.%m.%Y')} tarihine kaydırıldı."
                )
                veri_satiri = df_hisse_veri[df_hisse_veri["tarih"] == tarih2]
            else:
                log.warning(
                    f"{hisse_kodu_log} için {tarih.strftime('%d.%m.%Y')} ve "
                    "civarındaki fiyat verisi bulunamadı."
                )
                return np.nan

        if zaman_sutun_adi in veri_satiri.columns:
            fiyat = veri_satiri[zaman_sutun_adi].iloc[0]
            if pd.notna(fiyat):
                try:
                    return float(fiyat)
                except ValueError:
                    log.warning(
                        f"'{zaman_sutun_adi}' sütunundaki değer ('{fiyat}') "
                        f"float'a çevrilemedi. Hisse: {hisse_kodu_log}, Tarih: {tarih.strftime('%d.%m.%Y')}"
                    )
                    return np.nan
            return np.nan
        else:
            log.warning(
                f"Fiyat almak için beklenen sütun '{zaman_sutun_adi}' bulunamadı. "
                f"Hisse: {hisse_kodu_log}, Tarih: {tarih.strftime('%d.%m.%Y')}. "
                f"Mevcut Sütunlar: {df_hisse_veri.columns.tolist()}"
            )
            return np.nan
    except Exception as e:
        log.error(
            f"{hisse_kodu_log} için fiyat alınırken ({tarih.strftime('%d.%m.%Y')} {zaman_sutun_adi}) hata: {e}",
            exc_info=False,
        )
        return np.nan
