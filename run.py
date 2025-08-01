"""
Entry point for the backtest command-line interface.

This module orchestrates data loading, indicator calculation, filter
evaluation and Excel reporting. Invoke :func:`main` directly or run
``python -m finansal_analiz_sistemi``.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

import utils
from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.log_tools import ErrorCountingFilter, setup_logger
from finansal_analiz_sistemi.logging_config import get_logger
from utils.date_utils import parse_date

# Ensure mandatory indicators list is defined
if not hasattr(config, "CORE_INDICATORS") or not config.CORE_INDICATORS:
    logging.exception("Başlatma hatası: config.CORE_INDICATORS eksik veya boş.")
    raise RuntimeError(
        "CORE_INDICATORS eksik veya boş! Lütfen config.py dosyasını kontrol edin."
    )

logger = get_logger(__name__)
log_counter: ErrorCountingFilter | None = None

try:
    import backtest_core
    import data_loader
    import filter_engine
    import indicator_calculator
    import preprocessor
    import report_generator

    logger.info("Tüm ana modüller başarıyla import edildi.")
except ImportError as e_import_main:
    logger.critical(
        f"Temel modüllerden biri import edilemedi: {e_import_main}. Sistem durduruluyor.",
        exc_info=True,
    )
    raise ImportError(e_import_main)


def hazirla_rapor_tablolari(
    rapor_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """``rapor_df``'ten rapor tablolarını oluştur."""

    if rapor_df is None or rapor_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    ozet_df = rapor_df.copy()
    detay_df = rapor_df.copy()
    sayisal = rapor_df.select_dtypes(include="number")
    istatistik_df = sayisal.describe().reset_index()
    return ozet_df, detay_df, istatistik_df


def _run_gui(ozet_df: pd.DataFrame, detay_df: pd.DataFrame) -> None:
    """Display summary or detail tables in a Streamlit interface.

    Triggered by the ``--gui`` flag, this helper lets the user switch
    between summary, detail and basic chart views. Percentage columns are
    plotted when available.
    """
    import streamlit as st

    st.sidebar.title("Menü")
    sayfa = st.sidebar.radio("Sayfa", ("Özet", "Detay", "Grafik"))

    df_map = {"Özet": ozet_df, "Detay": detay_df}
    df_to_show = df_map.get(sayfa, ozet_df)

    if df_to_show.empty:
        msg = "Filtreniz hiçbir sonuç döndürmedi. Koşulları gevşetmeyi deneyin."
        st.warning(msg)
        print(msg)
        if "logger" in globals():
            logger.warning(msg)
        return

    if sayfa == "Özet":
        st.dataframe(ozet_df)
    elif sayfa == "Detay":
        st.dataframe(detay_df)
    else:
        if "ort_getiri_%" in ozet_df:
            st.bar_chart(ozet_df.set_index("filtre_kodu")["ort_getiri_%"])
        else:
            st.write("Grafik için veri yok")


def veri_yukle(
    force_excel_reload: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load filter definitions together with the raw price dataset.

    Parameters
    ----------
    force_excel_reload : bool, optional
        When ``True`` ignore cached Parquet data and reload the Excel files.

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame]
        ``(df_filters, df_raw)`` tuple containing filter rules and raw price
        data. The function exits the program when either dataset is missing.
    """

    df_filters = data_loader.yukle_filtre_dosyasi(logger_param=logger)
    if df_filters is None or df_filters.empty:
        logger.critical("Filtre kuralları yüklenemedi veya boş.")
        sys.exit(1)

    df_raw = data_loader.yukle_hisse_verileri(
        force_excel_reload=force_excel_reload, logger_param=logger
    )
    if df_raw is None or df_raw.empty:
        logger.critical("Hisse verileri yüklenemedi veya boş.")
        sys.exit(1)
    return df_filters, df_raw


def on_isle(df: pd.DataFrame) -> pd.DataFrame:
    """Return preprocessed stock data.

    Args:
        df (pd.DataFrame): Raw dataset loaded from disk.

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for indicator computation.
    """
    processed = preprocessor.on_isle_hisse_verileri(df, logger_param=logger)
    if processed is None or processed.empty:
        logger.critical("Veri ön işleme başarısız.")
        sys.exit(1)
    return processed


def indikator_hesapla(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate indicators and crossover columns.

    Args:
        df (pd.DataFrame): Preprocessed OHLCV dataset.

    Returns:
        pd.DataFrame: DataFrame enriched with indicator values and crossover
        signals.
    """
    wanted_cols = utils.extract_columns_from_filters_cached(
        df_filtre_kurallari.to_csv(index=False),
        tuple(config.SERIES_SERIES_CROSSOVERS),
        tuple(config.SERIES_VALUE_CROSSOVERS),
    )
    from utils.memory_profile import mem_profile

    with mem_profile():
        result = indicator_calculator.hesapla_teknik_indikatorler_ve_kesisimler(
            df,
            wanted_cols=wanted_cols,
            df_filters=df_filtre_kurallari,
            logger_param=logger,
        )
    if result is None:
        logger.critical("İndikatör hesaplanamadı.")
        sys.exit(1)
    return result


def filtre_uygula(df: pd.DataFrame, tarama_tarihi) -> tuple[dict, dict]:
    """Apply filter rules to indicator data.

    Args:
        df (pd.DataFrame): Indicator dataset.
        tarama_tarihi (datetime.datetime | pd.Timestamp): Screening date.

    Returns:
        tuple[dict, dict]: Filter results and skipped information.
    """
    return filter_engine.uygula_filtreler(
        df, df_filtre_kurallari, tarama_tarihi, logger_param=logger
    )


def backtest_yap(
    df: pd.DataFrame,
    filtre_sonuclari: dict,
    tarama_tarihi: str,
    satis_tarihi: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run a minimal backtest."""

    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        filtre_sonuc_dict=filtre_sonuclari,
        df_tum_veri=df,
        satis_tarihi_str=satis_tarihi,
        tarama_tarihi_str=tarama_tarihi,
        logger_param=logger,
    )
    if rapor_df is None:
        logger.critical("Backtest sonuç üretmedi.")
        sys.exit(1)
    return rapor_df, detay_df


def raporla(rapor_df: pd.DataFrame, detay_df: pd.DataFrame) -> None:
    """Save an Excel report when data is available.

    Args:
        rapor_df (pd.DataFrame): Summary table produced by the backtest.
        detay_df (pd.DataFrame): Detailed trade information.
    """
    if rapor_df.empty:
        logger.info("Rapor verisi boş.")
        return
    ozet, detay, istat = hazirla_rapor_tablolari(rapor_df)
    out_path = Path("raporlar") / f"rapor_{pd.Timestamp.now():%Y%m%d_%H%M%S}.xlsx"
    out_path.parent.mkdir(exist_ok=True)
    from utils.memory_profile import mem_profile

    with mem_profile():
        report_generator.kaydet_uc_sekmeli_excel(out_path, ozet, detay, istat)
    logger.info(f"Excel raporu oluşturuldu: {out_path}")


def run_pipeline(
    price_csv: str | Path,
    filter_def: str | Path,
    output: str | Path,
) -> Path:
    """Execute the end-to-end workflow and return the report location.

    Args:
        price_csv (str | Path): CSV file containing price data.
        filter_def (str | Path): YAML file defining filter clauses.
        output (str | Path): Destination path for the Excel workbook.

    Returns:
        Path: Absolute path of the generated Excel report.
    """
    global log_counter
    if log_counter is None:
        log_counter = setup_logger()
    df = pd.read_csv(
        price_csv,
        comment="#",
        header=None,
        names=["code", "date", "open", "high", "low", "close", "volume"],
        parse_dates=["date"],
    )
    df = df.rename(columns={"code": "hisse_kodu", "date": "tarih"})
    if not pd.api.types.is_datetime64_any_dtype(df["tarih"]):
        df["tarih"] = df["tarih"].apply(parse_date)

    with open(filter_def, encoding="utf-8") as f:
        filt = yaml.safe_load(f) or []
    filt_df = pd.DataFrame(filt).rename(
        columns={"code": "FilterCode", "clause": "PythonQuery"}
    )

    tarama_dt = df["tarih"].min()
    satis_dt = df["tarih"].max()

    filtre_sonuclar, _ = filter_engine.uygula_filtreler(df, filt_df, tarama_dt)
    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        filtre_sonuclar,
        df,
        satis_tarihi_str=satis_dt.strftime("%d.%m.%Y"),
        tarama_tarihi_str=tarama_dt.strftime("%d.%m.%Y"),
    )
    return report_generator.generate_full_report(rapor_df, detay_df, [], output)


def calistir_tum_sistemi(
    tarama_tarihi_str: str,
    satis_tarihi_str: str,
    force_excel_reload_param: bool = False,
    logger_param: Optional[logging.Logger] = None,
    output_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict | None]:
    """Run all analysis steps sequentially."""

    import gc

    import filter_engine
    import utils.failure_tracker as ft

    steps_report = []
    filter_engine.clear_failed()
    ft.clear_failures()

    rapor_df = detay_df = None
    atlanmis: dict | None = None

    global df_filtre_kurallari
    logger.info("*" * 30 + " TÜM BACKTEST SİSTEMİ ÇALIŞTIRILIYOR " + "*" * 30)

    try:
        logger.info("veri_yukle BAŞLIYOR")
        steps_report.append("veri_yukle: BAŞLADI")
        df_filtre_kurallari, df_raw = veri_yukle(force_excel_reload_param)
        steps_report.append("veri_yukle: BAŞARILI")

        logger.info("on_isle BAŞLIYOR")
        steps_report.append("on_isle: BAŞLADI")
        df_processed = on_isle(df_raw)
        steps_report.append("on_isle: BAŞARILI")

        logger.info("indikator_hesapla BAŞLIYOR")
        steps_report.append("indikator_hesapla: BAŞLADI")
        df_indicator = indikator_hesapla(df_processed)
        steps_report.append("indikator_hesapla: BAŞARILI")

        tarama_dt = parse_date(tarama_tarihi_str)

        logger.info("filtre_uygula BAŞLIYOR")
        steps_report.append("filtre_uygula: BAŞLADI")
        filtre_sonuclar, atlanmis = filtre_uygula(df_indicator, tarama_dt)
        steps_report.append("filtre_uygula: BAŞARILI")

        logger.info("backtest_yap BAŞLIYOR")
        steps_report.append("backtest_yap: BAŞLADI")
        rapor_df, detay_df = backtest_yap(
            df_indicator,
            filtre_sonuclar,
            tarama_tarihi_str,
            satis_tarihi_str,
        )
        steps_report.append("backtest_yap: BAŞARILI")

        if output_path:
            from report_generator import generate_full_report
            from utils.memory_profile import mem_profile

            output_path = Path(output_path)
            with mem_profile():
                generate_full_report(rapor_df.copy(), detay_df.copy(), [], output_path)
            if logger_param:
                logger_param.info("Saved report to %s", output_path)
        else:
            raporla(rapor_df, detay_df)

        steps_report.append("TÜM ADIMLAR TAMAMLANDI")
        logger.info("TÜM ADIMLAR BAŞARIYLA TAMAMLANDI")

    except Exception as e:
        traceback.print_exc()
        steps_report.append(f"HATA: {type(e).__name__}: {str(e)}")
        raise

    finally:
        logger.info("\n=== ADIM RAPORU ===")
        for adim in steps_report:
            logger.info(adim)
        logger.info("=== RAPOR SONU ===\n")
        gc.collect()

    return rapor_df, detay_df, atlanmis


def main(argv: list[str] | None = None) -> None:
    """Execute the main backtest workflow for CLI usage."""

    parser = argparse.ArgumentParser(description="Finansal analiz ve backtest")
    parser.add_argument(
        "--tarama",
        default=getattr(config, "TARAMA_TARIHI_DEFAULT", "2020-01-01"),
        help="dd.mm.yyyy formatında tarama tarihi",
    )
    parser.add_argument(
        "--satis",
        default=getattr(config, "SATIS_TARIHI_DEFAULT", "2020-12-31"),
        help="dd.mm.yyyy formatında satış tarihi",
    )
    parser.add_argument("--gui", action="store_true", help="Show a simple Streamlit UI")
    parser.add_argument(
        "--force-excel-reload",
        action="store_true",
        help="Reload Excel/CSV files instead of the Parquet cache",
    )
    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="Manually specify the settings.yaml path",
    )
    parser.add_argument("--output", required=True, help="Destination Excel .xlsx path")
    parser.add_argument("--ind-set", choices=["core", "full"], default="core")
    parser.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE)
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log seviyesi",
    )
    args = parser.parse_args(argv)

    try:
        from finansal_analiz_sistemi import settings_loader

        loaded_cfg = settings_loader.load_settings(args.settings_file)
        if loaded_cfg:
            logger.info("Yüklü ayarlar: %s", loaded_cfg)
    except Exception as exc:  # pragma: no cover - CLI safeguard
        print(exc)
        sys.exit(1)

    global log_counter
    log_counter = setup_logger(level=getattr(logging, args.log_level))

    logger.info("=" * 80)
    logger.info(
        f"======= {os.path.basename(__file__).upper()} ANA BACKTEST SCRIPT BAŞLIYOR ======="
    )

    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    tarama_t = args.tarama
    satis_t = args.satis

    full_inds = (
        config.CORE_INDICATORS
        + [f"ema_{n}" for n in (50, 100, 200)]
        + [f"sma_{n}" for n in (50, 100, 200)]
    )
    active_inds = config.CORE_INDICATORS if args.ind_set == "core" else full_inds
    logger.info("Aktif gosterge listesi: %s", ", ".join(active_inds))

    logger.info(f"  Tarama Tarihi    : {tarama_t}")
    logger.info(f"  Satış Tarihi     : {satis_t}")
    logger.info("=" * 80 + "\n")

    atlanmis: dict | None = {}
    try:
        rapor_df, detay_df, atlanmis = calistir_tum_sistemi(
            tarama_tarihi_str=tarama_t,
            satis_tarihi_str=satis_t,
            force_excel_reload_param=args.force_excel_reload,
            logger_param=logger,
            output_path=args.output,
        )

        if rapor_df.empty:
            empty_msg = (
                "Filtreniz hiçbir sonuç döndürmedi. Koşulları gevşetmeyi deneyin."
            )
            logger.warning(empty_msg)
            print(empty_msg)

        summary_df = rapor_df.copy()
        detail_df = detay_df.copy()
        error_list = atlanmis.get("hatalar", [])
        if not error_list:
            logging.warning("Uyarı: error_list boş—'Hatalar' sheet'i yazılmayacak!")

        rapor_path = report_generator.generate_full_report(
            summary_df,
            detail_df,
            error_list,
            out_file,
            keep_legacy=True,
        )
        print(f"Rapor oluşturuldu → {rapor_path}")

        if args.gui:
            _run_gui(rapor_df, detay_df)

    except Exception:
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info(
            f"======= {os.path.basename(__file__).upper()} ANA BACKTEST SCRIPT TAMAMLANDI ======="
        )
        summary_keys = [str(k) for k in atlanmis.keys() if k]
        summary_line = (
            f"LOG_SUMMARY | errors={log_counter.errors} | warnings={log_counter.warnings} | "
            f"atlanan_filtre={','.join(summary_keys)}"
        )
        logger.info(summary_line)
        if log_counter.errors > 0 and "rapor_path" in locals():
            from report_generator import add_error_sheet

            with pd.ExcelWriter(
                rapor_path, mode="a", if_sheet_exists="replace", engine="openpyxl"
            ) as wr:
                add_error_sheet(wr, log_counter.error_list)
        logging.shutdown()
        utils.purge_old_logs(log_dir="loglar", keep_days=30)


if __name__ == "__main__":  # pragma: no cover - manual execution
    print("RUN.PY CLI BAŞLATILDI")
    main()
