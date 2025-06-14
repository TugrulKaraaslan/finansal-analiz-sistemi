import os
from pathlib import Path
from datetime import datetime

import pandas as pd
from logger_setup import get_logger

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
    if logger:
        logger.info(f"Hisse bazlı detaylı rapor oluşturuldu: {dosya_adi}")
    return dosya_adi


def olustur_hatali_filtre_raporu(
    hatalar_listesi: list, cikti_klasoru: str, logger=None
):
    """'hatalar_listesi' elemanlarının 'filtre_kodu' ve 'notlar' anahtarları
    içerdiği varsayılır."""
    if not hatalar_listesi:
        return None
    os.makedirs(cikti_klasoru, exist_ok=True)
    df = pd.DataFrame(hatalar_listesi)
    dosya_adi = os.path.join(
        cikti_klasoru,
        f"hatali_filtre_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    )
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Hatalı filtre raporu oluşturuldu: {dosya_adi}")
    return dosya_adi


def olustur_excel_raporu(kayitlar: list[dict], fname: str | Path, logger=None):
    """Given summary records, save them into a single-sheet Excel file."""
    if not kayitlar:
        if logger:
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


if __name__ == "__main__":
    from pathlib import Path
    import log_to_health

    log_files = sorted(Path(".").glob("*.log"))
    excel_files = sorted(Path("cikti/raporlar").glob("rapor_*.xlsx"))
    if log_files and excel_files:
        log_to_health.generate(str(log_files[-1]), [str(excel_files[-1])])
