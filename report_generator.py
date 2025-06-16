import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import openpyxl
import report_utils
from utils.logging_setup import setup_logger, get_logger
import logging

setup_logger()
fn_logger = get_logger(__name__)


def olustur_ozet_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    """Sonuç listesinde beklenen anahtarlar: 'hisseler', 'notlar' ve
    her hisse için 'getiri_yuzde'."""
    if logger is None:
        logger = fn_logger
    os.makedirs(cikti_klasoru, exist_ok=True)
    ozet_kayitlar = []

    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            fn_logger.warning(f"Beklenmeyen sonuç tipi: {type(sonuc)} → {sonuc}")
            continue
        secilen_hisseler = sonuc.get("hisseler", [])
        if not secilen_hisseler:
            fn_logger.warning(
                f"Filtre '{sonuc.get('filtre_kodu', '?')}' sonucu: Hiç hisse seçilmedi. Boş rapor satırı yazılacak."
            )
        getiriler = [
            h.get("getiri_yuzde", 0)
            for h in secilen_hisseler
            if isinstance(h, dict) and h.get("getiri_yuzde") is not None
        ]
        ortalama_getiri = round(sum(getiriler) / len(getiriler), 2) if getiriler else 0
        ozet_kayitlar.append(
            {
                "filtre_kodu": sonuc.get("filtre_kodu", ""),
                "bulunan_hisse_sayisi": len(secilen_hisseler),
                "ortalama_getiri": ortalama_getiri,
                "notlar": sonuc.get("notlar", ""),
                "tarama_tarihi": sonuc.get("tarama_tarihi", ""),
                "satis_tarihi": sonuc.get("satis_tarihi", ""),
            }
        )

    df = pd.DataFrame(ozet_kayitlar)
    dosya_adi = os.path.join(
        cikti_klasoru, f"ozet_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    logger.info(f"Özet rapor oluşturuldu: {dosya_adi}")
    return dosya_adi


def olustur_hisse_bazli_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    """Her sonucun 'hisseler' listesinde 'alis_tarihi', 'satis_tarihi',
    'uygulanan_strateji' ve 'getiri_yuzde' alanları ile ana sözlükte 'notlar'
    anahtarlarını bekler."""
    if logger is None:
        logger = fn_logger
    os.makedirs(cikti_klasoru, exist_ok=True)
    detayli_kayitlar = []

    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            fn_logger.warning(f"Geçersiz filtre sonucu tipi: {type(sonuc)}")
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
        f"hisse_bazli_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    )
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    logger.info(f"Hisse bazlı detaylı rapor oluşturuldu: {dosya_adi}")
    return dosya_adi


def olustur_hatali_filtre_raporu(atlanmis_dict: dict, writer) -> pd.DataFrame | None:
    """Write skipped filter information into an Excel sheet named 'Hatalar'."""

    if not atlanmis_dict:
        return None

    df = pd.DataFrame(
        [(k, v) for k, v in atlanmis_dict.items()],
        columns=["filtre_kodu", "hata_mesaji"],
    )

    df.to_excel(writer, sheet_name="Hatalar", index=False)
    fn_logger.info("Hatalı filtre raporu Excel'e yazıldı.")
    return df


def olustur_excel_raporu(kayitlar: list[dict], fname: str | Path, logger=None):
    """Given summary records, save them into a single-sheet Excel file."""
    if logger is None:
        logger = fn_logger
    if not kayitlar:
        logger.warning("Hiç kayıt yok – Excel raporu atlandı.")
        return None

    rapor_df = pd.DataFrame(kayitlar).sort_values("filtre_kodu")
    return kaydet_uc_sekmeli_excel(fname, rapor_df, pd.DataFrame(), pd.DataFrame())


def kaydet_uc_sekmeli_excel(
    fname: str,
    ozet_df: pd.DataFrame,
    detay_df: pd.DataFrame,
    istatistik_df: pd.DataFrame,
):
    """Üç DataFrame'i tek seferde aynı Excel dosyasına kaydet."""

    os.makedirs(os.path.dirname(fname) or ".", exist_ok=True)

    with pd.ExcelWriter(
        fname,
        engine="xlsxwriter",
        mode="w",
    ) as w:
        ozet_df.to_excel(w, sheet_name="Özet", index=False)
        detay_df.to_excel(w, sheet_name="Detay", index=False)
        istatistik_df.to_excel(w, sheet_name="İstatistik", index=False)

    return fname


def kaydet_raporlar(
    ozet_df: pd.DataFrame,
    detay_df: pd.DataFrame,
    istat_df: pd.DataFrame,
    filepath: Path,
):
    """Append summary, detail and statistics sheets to an existing Excel file."""

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

    fn_logger.info(f"Rapor kaydedildi → {filepath}")

    return filepath


def generate_full_report(sonuc_dict: dict, out_xlsx: str | Path) -> Path:
    """Build dataframes from results and write a four-sheet Excel report."""
    summary_df = sonuc_dict.get("summary")
    detail_df = sonuc_dict.get("detail")
    tarama_tarihi = sonuc_dict.get("tarama_tarihi", "")
    satis_tarihi = sonuc_dict.get("satis_tarihi", "")

    if summary_df is None or getattr(summary_df, "empty", False):
        out_xlsx = Path(out_xlsx)
        out_xlsx.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(
            out_xlsx,
            engine="openpyxl",
            engine_kwargs={"write_only": True},
            mode="w",
        ) as w:
            wb = w.book
            ws = wb.create_sheet("Uyari")
            ws.append(["Uyari"])
            ws.append(["Filtre bulunamadi"])
            w.sheets["Uyari"] = ws
        return out_xlsx

    ozet_df = report_utils.build_ozet_df(
        summary_df, detail_df, tarama_tarihi, satis_tarihi
    )
    detay_df = report_utils.build_detay_df(summary_df, detail_df)
    stats_df = report_utils.build_stats_df(ozet_df)

    out_xlsx = Path(out_xlsx)
    out_xlsx.parent.mkdir(parents=True, exist_ok=True)

    from openpyxl.utils.dataframe import dataframe_to_rows

    with pd.ExcelWriter(
        out_xlsx,
        engine="openpyxl",
        engine_kwargs={"write_only": True},
        mode="w",
    ) as w:
        wb = w.book

        ws_ozet = wb.create_sheet("Özet")
        for r in dataframe_to_rows(ozet_df, index=False, header=True):
            ws_ozet.append(r)
        w.sheets["Özet"] = ws_ozet

        ws_detay = wb.create_sheet("Detay")
        for r in dataframe_to_rows(detay_df, index=False, header=True):
            ws_detay.append(r)
        w.sheets["Detay"] = ws_detay

        ws_stats = wb.create_sheet("İstatistik")
        for r in dataframe_to_rows(stats_df, index=False, header=True):
            ws_stats.append(r)
        w.sheets["İstatistik"] = ws_stats

    wb = openpyxl.load_workbook(out_xlsx)
    ws_sum = wb["Özet"]
    report_utils.add_bar_chart(ws_sum, data_col=3, label_col=1, title="En İyi 10 Ortalama Getiri")
    wb.save(out_xlsx)

    return out_xlsx

if __name__ == "__main__":
    from pathlib import Path
    import log_to_health

    log_files = sorted(Path(".").glob("*.log"))
    excel_files = sorted(Path("cikti/raporlar").glob("rapor_*.xlsx"))
    if log_files and excel_files:
        log_to_health.generate(str(log_files[-1]), [str(excel_files[-1])])
