import pandas as pd
import os
from logger_setup import get_logger
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill
fn_logger = get_logger(__name__)

def olustur_ozet_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    """Sonuç listesinde beklenen anahtarlar: 'hisseler', 'notlar' ve
    her hisse için 'getiri_yuzde'."""
    os.makedirs(cikti_klasoru, exist_ok=True)
    ozet_kayitlar = []

    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            fn_logger.warning(f"Beklenmeyen sonuç tipi: {type(sonuc)} → {sonuc}")
            continue
        secilen_hisseler = sonuc.get("hisseler", [])
        if not secilen_hisseler:
            fn_logger.warning(f"Filtre '{sonuc.get('filtre_kodu', '?')}' sonucu: Hiç hisse seçilmedi. Boş rapor satırı yazılacak.")
        getiriler = [h.get("getiri_yuzde", 0) for h in secilen_hisseler if isinstance(h, dict) and h.get("getiri_yuzde") is not None]
        ortalama_getiri = round(sum(getiriler) / len(getiriler), 2) if getiriler else 0
        ozet_kayitlar.append({
            "filtre_kodu": sonuc.get("filtre_kodu", ""),
            "bulunan_hisse_sayisi": len(secilen_hisseler),
            "ortalama_getiri": ortalama_getiri,
            "notlar": sonuc.get("notlar", ""),
            "tarama_tarihi": sonuc.get("tarama_tarihi", ""),
            "satis_tarihi": sonuc.get("satis_tarihi", "")
        })

    df = pd.DataFrame(ozet_kayitlar)
    dosya_adi = os.path.join(cikti_klasoru, f"ozet_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Özet rapor oluşturuldu: {dosya_adi}")
    return dosya_adi

def olustur_hisse_bazli_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    """Her sonucun 'hisseler' listesinde 'alis_tarihi', 'satis_tarihi',
    'uygulanan_strateji' ve 'getiri_yuzde' alanları ile ana sözlükte 'notlar'
    anahtarlarını bekler."""
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
            detayli_kayitlar.append({
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
                "tarama_ortalama": tarama_ortalama
            })
    if not detayli_kayitlar:
        return None
    df = pd.DataFrame(detayli_kayitlar)
    dosya_adi = os.path.join(cikti_klasoru, f"hisse_bazli_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Hisse bazlı detaylı rapor oluşturuldu: {dosya_adi}")
    return dosya_adi

def olustur_hatali_filtre_raporu(hatalar_listesi: list, cikti_klasoru: str, logger=None):
    """'hatalar_listesi' elemanlarının 'filtre_kodu' ve 'notlar' anahtarları
    içerdiği varsayılır."""
    if not hatalar_listesi:
        return None
    os.makedirs(cikti_klasoru, exist_ok=True)
    df = pd.DataFrame(hatalar_listesi)
    dosya_adi = os.path.join(cikti_klasoru, f"hatali_filtre_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Hatalı filtre raporu oluşturuldu: {dosya_adi}")
    return dosya_adi


def _apply_return_formatting(ws, column_letter: str, max_row: int) -> None:
    """Apply conditional formatting on return percentage columns."""
    positive_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
    negative_fill = PatternFill(start_color="FF7F7F", end_color="FF7F7F", fill_type="solid")
    zero_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")

    cell_range = f"{column_letter}2:{column_letter}{max_row}"
    ws.conditional_formatting.add(cell_range, CellIsRule(operator='greaterThan', formula=['0'], fill=positive_fill))
    ws.conditional_formatting.add(cell_range, CellIsRule(operator='lessThan', formula=['0'], fill=negative_fill))
    ws.conditional_formatting.add(cell_range, CellIsRule(operator='equal', formula=['0'], fill=zero_fill))


def olustur_excel_raporu(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    """Create an Excel report with summary, detail and general sheets."""
    os.makedirs(cikti_klasoru, exist_ok=True)

    summary_records = []
    detail_records = []

    for sonuc in sorted(sonuclar_listesi, key=lambda x: x.get("filtre_kodu", "")):
        hisseler = sonuc.get("hisseler", []) or []
        notlar = sonuc.get("notlar", [])
        if isinstance(notlar, list):
            note_text = "; ".join(notlar)
        else:
            note_text = str(notlar)
        if not hisseler:
            note_text = note_text or "Bu filtreye uygun hisse yok"

        getiriler = [h.get("getiri_yuzde") for h in hisseler if isinstance(h, dict) and h.get("getiri_yuzde") is not None]
        avg_ret = round(sum(getiriler) / len(getiriler), 2) if getiriler else 0
        max_ret = round(max(getiriler), 2) if getiriler else 0
        min_ret = round(min(getiriler), 2) if getiriler else 0

        summary_records.append({
            "Filtre Kodu": sonuc.get("filtre_kodu", ""),
            "Bulunan Hisse": len(hisseler),
            "İşlemli": "EVET" if hisseler else "HAYIR",
            "Ortalama Getiri (%)": avg_ret,
            "En Yüksek Getiri (%)": max_ret,
            "En Düşük Getiri (%)": min_ret,
            "Notlar": note_text,
            "Tarama Tarihi": sonuc.get("tarama_tarihi", ""),
            "Satış Tarihi": sonuc.get("satis_tarihi", ""),
        })

        for hisse in sorted(hisseler, key=lambda h: h.get("hisse_kodu", "")):
            detail_records.append({
                "Filtre Kodu": sonuc.get("filtre_kodu", ""),
                "Hisse Kodu": hisse.get("hisse_kodu", ""),
                "Alış Tarihi": hisse.get("alis_tarihi", ""),
                "Satış Tarihi": hisse.get("satis_tarihi", ""),
                "Alış Fiyatı": hisse.get("alis_fiyati", ""),
                "Satış Fiyatı": hisse.get("satis_fiyati", ""),
                "Getiri (%)": hisse.get("getiri_yuzde", ""),
                "Uygulanan Strateji": hisse.get("uygulanan_strateji", ""),
                "Genel Tarama Tarihi": sonuc.get("tarama_tarihi", ""),
                "Genel Satış Tarihi": sonuc.get("satis_tarihi", ""),
            })

    df_summary = pd.DataFrame(summary_records).sort_values("Filtre Kodu")
    df_detail = pd.DataFrame(detail_records).sort_values(["Filtre Kodu", "Hisse Kodu"])

    total_filters = len(df_summary)
    transaction_filters = (df_summary["Bulunan Hisse"] > 0).sum()
    fail_ratio = round(((df_summary["Bulunan Hisse"] == 0).sum() / total_filters) * 100, 2) if total_filters else 0
    success_ratio = round(((df_summary["Ortalama Getiri (%)"] > 0).sum() / total_filters) * 100, 2) if total_filters else 0
    mean_return = round(df_summary["Ortalama Getiri (%)"].mean(), 2) if total_filters else 0

    df_general = pd.DataFrame([
        {
            "Toplam Filtre": total_filters,
            "İşlemli Filtre Sayısı": transaction_filters,
            "Başarısız Filtre Oranı (%)": fail_ratio,
            "Genel Başarı Oranı (%)": success_ratio,
            "Genel Ortalama Getiri (%)": mean_return,
        }
    ])

    dosya_adi = os.path.join(cikti_klasoru, f"rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    with pd.ExcelWriter(dosya_adi, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Filtre_Ozet", index=False)
        df_detail.to_excel(writer, sheet_name="Hisse_Detay", index=False)
        df_general.to_excel(writer, sheet_name="Genel_Performans", index=False)

    wb = load_workbook(dosya_adi)

    ws_summary = wb["Filtre_Ozet"]
    ret_cols_sum = ["Ortalama Getiri (%)", "En Yüksek Getiri (%)", "En Düşük Getiri (%)"]
    for col in ret_cols_sum:
        idx = df_summary.columns.get_loc(col) + 1
        _apply_return_formatting(ws_summary, get_column_letter(idx), ws_summary.max_row)

    ws_detail = wb["Hisse_Detay"]
    if not df_detail.empty:
        idx = df_detail.columns.get_loc("Getiri (%)") + 1
        _apply_return_formatting(ws_detail, get_column_letter(idx), ws_detail.max_row)

    wb.save(dosya_adi)
    if logger:
        logger.info(f"Excel raporu oluşturuldu: {dosya_adi}")
    return dosya_adi
