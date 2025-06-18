from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime
from typing import Iterable

import pandas as pd
from openpyxl.utils import get_column_letter
from utils.logging_setup import get_logger, setup_logger

setup_logger()
fn_logger = get_logger(__name__)

LEGACY_SUMMARY_COLS = [
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

LEGACY_DETAIL_COLS = [
    "filtre_kodu",
    "hisse_kodu",
    "getiri_%",
    "basari",
    "strateji",
    "sebep_kodu",
]


def add_error_sheet(writer, error_list: Iterable[tuple]):
    if error_list:
        pd.DataFrame(
            error_list,
            columns=["timestamp", "level", "message"],
        ).to_excel(writer, sheet_name="Hatalar", index=False)


def olustur_ozet_rapor(
    sonuclar_listesi: list,
    cikti_klasoru: str,
    logger=None,
) -> str | None:
    if logger is None:
        logger = fn_logger
    os.makedirs(cikti_klasoru, exist_ok=True)
    kayitlar = []
    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            logger.warning(
                "Beklenmeyen sonuç tipi: %s → %s",
                type(sonuc),
                sonuc,
            )
            continue
        secilen = sonuc.get("hisseler", [])
        if not secilen:
            logger.warning(
                "Filtre '%s' sonucu: Hiç hisse seçilmedi."
                " Boş rapor satırı yazılacak.",
                sonuc.get("filtre_kodu", "?"),
            )
        getiriler = [
            h.get("getiri_yuzde", 0)
            for h in secilen
            if isinstance(h, dict) and h.get("getiri_yuzde") is not None
        ]
        ort = round(sum(getiriler) / len(getiriler), 2) if getiriler else 0
        kayitlar.append(
            {
                "filtre_kodu": sonuc.get("filtre_kodu", ""),
                "bulunan_hisse_sayisi": len(secilen),
                "ortalama_getiri": ort,
                "notlar": sonuc.get("notlar", ""),
                "tarama_tarihi": sonuc.get("tarama_tarihi", ""),
                "satis_tarihi": sonuc.get("satis_tarihi", ""),
            }
        )
    if not kayitlar:
        return None
    df = pd.DataFrame(kayitlar)
    dosya_adi = os.path.join(
        cikti_klasoru,
        f"ozet_rapor_{datetime.now():%Y%m%d_%H%M%S}.csv",
    )
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    logger.info("Özet rapor oluşturuldu: %s", dosya_adi)
    return dosya_adi


def olustur_hisse_bazli_rapor(
    sonuclar_listesi: list,
    cikti_klasoru: str,
    logger=None,
) -> str | None:
    if logger is None:
        logger = fn_logger
    os.makedirs(cikti_klasoru, exist_ok=True)
    detayli_kayitlar = []
    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            logger.warning("Geçersiz filtre sonucu tipi: %s", type(sonuc))
            continue
        filtre_kodu = sonuc.get("filtre_kodu", "")
        notlar = sonuc.get("notlar", "")
        tarama_ortalama = sonuc.get("tarama_ortalama", "")
        tarama_tarihi = sonuc.get("tarama_tarihi", "")
        satis_tarihi = sonuc.get("satis_tarihi", "")
        secilenler = sonuc.get("hisseler", [])
        for hisse in secilenler:
            if not isinstance(hisse, dict):
                continue
            detayli_kayitlar.append(
                {
                    "filtre_kodu": filtre_kodu,
                    "hisse_kodu": hisse.get("hisse_kodu", ""),
                    "alis_tarihi": hisse.get("alis_tarihi", ""),
                    "satis_tarihi": hisse.get("satis_tarihi", ""),
                    "alis_fiyati": hisse.get("alis_fiyati", ""),
                    "satis_fiyati": hisse.get("satis_fiyati", ""),
                    "getiri_yuzde": hisse.get("getiri_yuzde", ""),
                    "uygulanan_strateji": hisse.get("uygulanan_strateji", ""),
                    "tarama_tarihi": tarama_tarihi,
                    "satis_tarihi_genel": satis_tarihi,
                    "notlar": notlar,
                    "tarama_ortalama": tarama_ortalama,
                }
            )
    if not detayli_kayitlar:
        return None
    df = pd.DataFrame(detayli_kayitlar)
    dosya_adi = os.path.join(
        cikti_klasoru,
        f"hisse_bazli_rapor_{datetime.now():%Y%m%d_%H%M%S}.csv",
    )
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    logger.info("Hisse bazlı detaylı rapor oluşturuldu: %s", dosya_adi)
    return dosya_adi


def olustur_hatali_filtre_raporu(writer, kontrol_df: pd.DataFrame) -> None:
    sorunlu = kontrol_df[
        kontrol_df["durum"].isin(["CALISTIRILAMADI", "HATA", "DATASIZ"])
    ]
    cols = [
        "kod",
        "durum",
        "sebep",
        "eksik_sutunlar",
        "nan_sutunlar",
        "secim_adedi",
    ]
    sorunlu = sorunlu[cols]
    sheet_name = "Hatalar"
    sorunlu.to_excel(writer, sheet_name=sheet_name, index=False)
    ws = writer.sheets[sheet_name]
    if hasattr(ws, "set_column"):
        for i, col in enumerate(sorunlu.columns):
            max_len = max(10, sorunlu[col].astype(str).str.len().max() + 2)
            ws.set_column(i, i, max_len)
    else:
        for i, col in enumerate(sorunlu.columns, 1):
            max_len = max(10, sorunlu[col].astype(str).str.len().max() + 2)
            ws.column_dimensions[get_column_letter(i)].width = max_len


def olustur_excel_raporu(
    kayitlar: list[dict],
    fname: str | Path,
    logger=None,
) -> str | None:
    if logger is None:
        logger = fn_logger
    if not kayitlar:
        logger.warning("Hiç kayıt yok – Excel raporu atlandı.")
        return None
    rapor_df = pd.DataFrame(kayitlar).sort_values("filtre_kodu")
    return kaydet_uc_sekmeli_excel(
        fname,
        rapor_df,
        pd.DataFrame(),
        pd.DataFrame(),
    )


def kaydet_uc_sekmeli_excel(
    fname: str | Path,
    ozet_df: pd.DataFrame,
    detay_df: pd.DataFrame,
    istatistik_df: pd.DataFrame,
) -> str:
    os.makedirs(os.path.dirname(str(fname)) or ".", exist_ok=True)
    with pd.ExcelWriter(fname, engine="xlsxwriter", mode="w") as w:
        ozet_df.to_excel(w, sheet_name="Özet", index=False)
        detay_df.to_excel(w, sheet_name="Detay", index=False)
        istatistik_df.to_excel(w, sheet_name="İstatistik", index=False)
    return str(fname)


def kaydet_raporlar(
    ozet_df: pd.DataFrame,
    detay_df: pd.DataFrame,
    istat_df: pd.DataFrame,
    filepath: Path,
) -> Path:
    filepath = Path(filepath)
    with pd.ExcelWriter(
        filepath,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as w:
        ozet_df.to_excel(w, sheet_name="Özet", index=False)
        detay_df.to_excel(w, sheet_name="Detay", index=False)
        istat_df.to_excel(w, sheet_name="İstatistik", index=False)
    fn_logger.info("Rapor kaydedildi → %s", filepath)
    return filepath


def _write_stats_sheet(wr: pd.ExcelWriter, df: pd.DataFrame) -> None:
    stats = {
        "toplam_filtre": len(df),
        "işlemli": int(df["islemli"].sum()),
        "işlemsiz": int((df["islemli"] == 0).sum()),
        "genel_ortalama_%": df["ort_getiri_%"].mean(),
    }
    pd.DataFrame([stats]).to_excel(
        excel_writer=wr,
        sheet_name="İstatistik",
        index=False,
    )


def _write_error_sheet(wr: pd.ExcelWriter, error_list: Iterable) -> None:
    err_df = pd.DataFrame(error_list)
    err_df.to_excel(wr, "Hatalar", index=False)


def generate_full_report(
    summary_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    error_list: Iterable,
    out_path: str | Path,
    *,
    keep_legacy: bool = True,
) -> str:
    if keep_legacy:
        summary_df = summary_df.reindex(columns=LEGACY_SUMMARY_COLS)
        detail_df = detail_df.reindex(columns=LEGACY_DETAIL_COLS)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as wr:
        summary_df.to_excel(
            excel_writer=wr,
            sheet_name="Özet",
            index=False,
        )
        detail_df.to_excel(
            excel_writer=wr,
            sheet_name="Detay",
            index=False,
        )
        _write_stats_sheet(wr, summary_df)
        _write_error_sheet(wr, error_list)
    fn_logger.info("Rapor kaydedildi → %s", out_path)
    return str(out_path)


__all__ = [
    "add_error_sheet",
    "olustur_ozet_rapor",
    "olustur_hisse_bazli_rapor",
    "olustur_hatali_filtre_raporu",
    "olustur_excel_raporu",
    "kaydet_uc_sekmeli_excel",
    "kaydet_raporlar",
    "generate_full_report",
    "_write_stats_sheet",
    "_write_error_sheet",
]
