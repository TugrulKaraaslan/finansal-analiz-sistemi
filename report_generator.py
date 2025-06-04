import pandas as pd
import os
from logger_setup import get_logger
from datetime import datetime
fn_logger = get_logger(__name__)

def olustur_ozet_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
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
                "toplam_hisse": len(secilen_hisseler),
                "ortalama_getiri": ortalama_getiri,
                "notlar": ";".join(sonuc.get("notlar", [])),
                "tarama_tarihi": sonuc.get("tarama_tarihi", ""),
                "satis_tarihi": sonuc.get("satis_tarihi", ""),
            }
        )

    df = pd.DataFrame(ozet_kayitlar)
    dosya_adi = os.path.join(cikti_klasoru, f"ozet_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Özet rapor oluşturuldu: {dosya_adi}")
    return dosya_adi

def olustur_hisse_bazli_rapor(sonuclar_listesi: list, cikti_klasoru: str, logger=None):
    os.makedirs(cikti_klasoru, exist_ok=True)
    detayli_kayitlar = []

    for sonuc in sonuclar_listesi:
        if not isinstance(sonuc, dict):
            fn_logger.warning(f"Geçersiz filtre sonucu tipi: {type(sonuc)}")
            continue
        filtre_kodu = sonuc.get("filtre_kodu", "")
        notlar = ";".join(sonuc.get("notlar", []))
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
                "satis_tarihi_global": satis_tarihi,
                "not": notlar,
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
    if not hatalar_listesi:
        return None
    os.makedirs(cikti_klasoru, exist_ok=True)
    df = pd.DataFrame(hatalar_listesi)
    dosya_adi = os.path.join(cikti_klasoru, f"hatali_filtre_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    if logger:
        logger.info(f"Hatalı filtre raporu oluşturuldu: {dosya_adi}")
    return dosya_adi
