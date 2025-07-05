# filter_engine.py
# -*- coding: utf-8 -*-
# Proje: Finansal Analiz ve Backtest Sistemi Geliştirme
# Modül: Filtreleme Motoru
# Tuğrul Karaaslan & Gemini
# Tarih: 18 Mayıs 2025 (Loglama ve hata yönetimi iyileştirmeleri)

import keyword
import os
import re
from typing import Any, Iterable

import pandas as pd
import yaml
from pandas.errors import UndefinedVariableError as QueryError

import settings
from logging_config import get_logger


class MissingColumnError(Exception):
    """Raised when a required column is absent."""

    def __init__(self, missing: str):
        super().__init__(missing)
        self.missing = missing


def _extract_query_columns(query: str) -> set:
    query = re.sub(r"(?:'[^']*'|\"[^\"]*\")", " ", query)
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query))
    reserved = set(keyword.kwlist) | {"and", "or", "not", "True", "False", "df"}
    return tokens - reserved


def _extract_columns_from_query(query: str) -> set:
    """Yeni isimlendirme için yardımcı."""
    return _extract_query_columns(query)


logger = get_logger(__name__)

# Konfigürasyon dosyasından minimum hisse eşiğini oku
_cfg_path = os.path.join(os.path.dirname(__file__), "config.yml")
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        _cfg = yaml.safe_load(f) or {}
else:
    _cfg = {}
MIN_STOCKS_PER_FILTER = _cfg.get("min_stocks_per_filter", 1)

# Regular expressions for error parsing
_missing_re = re.compile(r"Eksik sütunlar?:\s*(?P<col>[A-Za-z0-9_]+)")
_undefined_re = re.compile(r"Tanımsız sütun/değişken:\s*'(?P<col>[^']+)'")

# Recursion guard
FAILED_FILTERS: list[dict] = []


def clear_failed() -> None:
    """Clear global FAILED_FILTERS list."""
    FAILED_FILTERS.clear()


class CircularError(QueryError):
    """Raised when a circular filter reference is detected."""


class CyclicFilterError(RuntimeError):
    """Raised when a cycle is found during filter evaluation."""


class MaxDepthError(RuntimeError):
    """Raised when maximum recursion depth is exceeded."""


FILTER_DEFS: dict[str, dict] = {}


def apply_filter_logic(fid: str) -> Any:
    """Placeholder logic for filter execution."""
    return fid


def _build_solution(err_type: str, msg: str) -> str:
    if err_type == "GENERIC":
        m1 = _missing_re.search(msg)
        if m1:
            col = m1.group("col")
            return f'"{col}" indikatörünü hesaplama listesine ekleyin.'
        m2 = _undefined_re.search(msg)
        if m2:
            col = m2.group("col")
            return f'Sorguda geçen "{col}" sütununu veri setine ekleyin veya sorgudan çıkarın.'
        return "Eksik veriyi veya sorgu değişkenini düzeltin."
    if err_type == "QUERY_ERROR":
        return "Query ifadesini pandas.query() sözdizimine göre düzeltin."
    if err_type == "NO_STOCK":
        return "Filtre koşullarını gevşetin veya tarih aralığını genişletin."
    return ""


def evaluate_filter(fid: str, depth: int = 0, seen: set[str] | None = None) -> Any:
    """Recursively evaluate filter tree by ``fid``.

    Raises ``CyclicFilterError`` when a cycle is detected and ``MaxDepthError``
    when ``settings.MAX_FILTER_DEPTH`` is exceeded.
    """

    seen = seen or set()
    if fid in seen:
        raise CyclicFilterError(f"Cyclic dependency → {' > '.join(list(seen) + [fid])}")
    if depth > settings.MAX_FILTER_DEPTH:
        raise MaxDepthError(f"Depth {depth} exceeded on {fid}")

    node = FILTER_DEFS.get(fid)
    if node is None:
        raise KeyError(f"Unknown filter: {fid}")

    seen.add(fid)
    for child in node.get("children", []):
        evaluate_filter(child, depth + 1, seen)
    return apply_filter_logic(fid)


def safe_eval(expr, df, depth: int = 0, visited=None):
    """Evaluate filter safely with depth and circular guards."""
    if visited is None:
        visited = set()
    if depth > settings.MAX_FILTER_DEPTH:
        raise QueryError(f"Max recursion depth ({settings.MAX_FILTER_DEPTH}) exceeded")

    if isinstance(expr, str):
        return df.query(expr)

    if isinstance(expr, dict) and "sub_expr" in expr:
        current = expr.get("code")
        if current is not None:
            if current in visited:
                raise CircularError(f"Circular reference: {current}")
            visited.add(current)
        try:
            return safe_eval(expr["sub_expr"], df, depth + 1, visited)
        except QueryError as e:
            FAILED_FILTERS.append({"filtre_kodu": expr.get("code"), "hata": str(e)})
            logger.warning("QUERY_ERROR %s", e)
            try:
                from utils.error_map import get_reason_hint
                from utils.failure_tracker import log_failure

                reason, hint = get_reason_hint(e)
                log_failure("filters", expr.get("code", "unknown"), reason, hint)
            except Exception:
                pass
            raise

    raise QueryError("Invalid expression")


def _apply_single_filter(df, kod, query):
    """Tek filtre sorgusunu çalıştır ve detaylı info döndür."""
    info = {
        "kod": kod,
        "tip": "tarama",
        "durum": None,
        "sebep": "",
        "eksik_sutunlar": "",
        "nan_sutunlar": "",
        "secim_adedi": 0,
    }

    try:
        from .utils import _extract_columns as _cols  # type: ignore
    except Exception:  # pragma: no cover - fallback for non-package usage
        try:
            from .utils import _extract_columns_from_query as _cols  # type: ignore
        except Exception:
            _cols = _extract_columns_from_query

    req_cols = _cols(query)
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        info.update(
            durum="CALISTIRILAMADI",
            sebep="EXIST_FALSE",
            eksik_sutunlar=",".join(missing),
        )
        return None, info

    nan_cols = [c for c in req_cols if df[c].isna().mean() > 0.9]
    if nan_cols:
        info.update(
            durum="DATASIZ",
            sebep="NAN_GT90",
            nan_sutunlar=",".join(nan_cols),
        )

    try:
        seç = df.query(query)
        # --- 0 hisse skip mekaniği ---
        if len(seç) < MIN_STOCKS_PER_FILTER:
            logger.debug(
                "Filter %s skipped (len=%s < %s)",
                kod,
                len(seç),
                MIN_STOCKS_PER_FILTER,
            )
            info.update(durum="BOS", sebep="SIFIR_HISSE")
            return pd.DataFrame(), info

        info["secim_adedi"] = len(seç)
        if len(seç):
            info.update(durum="OK", sebep="HISSE_BULUNDU")
        else:
            if info["durum"] is None:
                info.update(durum="BOS", sebep="SIFIR_HISSE")
        return seç, info
    except Exception as e:
        info.update(durum="HATA", sebep=str(e)[:120])
        try:
            from utils.error_map import get_reason_hint
            from utils.failure_tracker import log_failure

            reason, hint = get_reason_hint(e)
            log_failure("filters", kod, reason, hint)
        except Exception:
            pass
        return None, info


def run_filter(code, df, expr):
    """Simple wrapper for running a filter expression."""
    # Pasif filtreler listede mi?
    from config import cfg

    if code in cfg.get("passive_filters", []):
        logger.info("Filter %s marked passive, skipped.", code)
        return pd.DataFrame()
    return safe_eval(expr, df)


def run_single_filter(kod: str, query: str) -> dict:
    """Küçük bir DataFrame üzerinde tek filtreyi çalıştır."""
    df = pd.DataFrame({"close": [1]})
    atlanmis: dict = {}
    try:
        df.query(query)
    except QueryError as qe:
        msg = str(qe)
        atlanmis.setdefault("hatalar", []).append(
            {
                "filtre_kod": kod,
                "hata_tipi": "QUERY_ERROR",
                "detay": msg,
                "cozum_onerisi": _build_solution("QUERY_ERROR", msg),
            }
        )
        logger.warning(f"QUERY_ERROR: {kod} – {msg}")
        try:
            from utils.error_map import get_reason_hint
            from utils.failure_tracker import log_failure

            reason, hint = get_reason_hint(qe)
            log_failure("filters", kod, reason, hint)
        except Exception:
            pass
    except MissingColumnError as me:
        msg = str(me)
        atlanmis.setdefault("hatalar", []).append(
            {
                "filtre_kod": kod,
                "hata_tipi": "GENERIC",
                "eksik_ad": me.missing,
                "detay": msg,
                "cozum_onerisi": _build_solution("GENERIC", msg),
            }
        )
        logger.warning(f"GENERIC: {kod} – {msg}")
        try:
            from utils.error_map import get_reason_hint
            from utils.failure_tracker import log_failure

            reason, hint = get_reason_hint(me)
            log_failure("filters", kod, reason, hint)
        except Exception:
            pass
    return atlanmis


def uygula_filtreler(
    df_ana_veri: pd.DataFrame,
    df_filtre_kurallari: pd.DataFrame,
    tarama_tarihi: pd.Timestamp,
    logger_param=None,
) -> tuple[dict, dict]:
    """
    Verilen ana veri üzerinde, filtre kurallarını kullanarak hisseleri tarar.

    Args:
        df_ana_veri (pd.DataFrame): İndikatörleri hesaplanmış tüm hisse verilerini içeren DataFrame.
        df_filtre_kurallari (pd.DataFrame): 'FilterCode' ve 'PythonQuery' sütunlarını içeren DataFrame.
        tarama_tarihi (pd.Timestamp): Hangi tarihteki verilere göre tarama yapılacağı.
        logger_param: Kullanılacak logger nesnesi (opsiyonel).

    Returns:
        tuple[dict, dict]:
            - filtre_sonuclar: {
                filtre_kodu: {
                    "hisseler": list[str],
                    "sebep": str,
                    "hisse_sayisi": int,
                }
            }
            - atlanmis_filtreler_log_dict: {filtre_kodu: hata_mesajı}
    """
    if logger_param is None:
        logger_param = logger
    fn_logger = logger_param
    fn_logger.info(
        f"Filtreleme işlemi başlatılıyor. Tarama Tarihi: {tarama_tarihi.strftime('%d.%m.%Y')}"
    )

    if df_ana_veri is None or df_ana_veri.empty:
        fn_logger.error(
            "Filtreleme için ana veri (df_ana_veri) boş veya None. İşlem durduruluyor."
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": "Filtreleme için ana veri (df_ana_veri) boş veya None."
        }

    if "hisse_kodu" not in df_ana_veri.columns or "tarih" not in df_ana_veri.columns:
        fn_logger.error(
            f"Ana veride 'hisse_kodu' veya 'tarih' sütunları eksik. Filtreleme yapılamaz. Mevcut sütunlar: {df_ana_veri.columns.tolist()}"
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": "Ana veride hisse_kodu veya tarih sütunu eksik."
        }

    try:
        # Tarih sütununun datetime olduğundan emin ol
        if not pd.api.types.is_datetime64_any_dtype(df_ana_veri["tarih"]):
            df_ana_veri["tarih"] = pd.to_datetime(df_ana_veri["tarih"], errors="coerce")

        # Sadece tarama gününe ait veriyi al ve üzerinde çalışmak için kopyala
        df_tarama_gunu = df_ana_veri[df_ana_veri["tarih"] == tarama_tarihi].copy()
        if df_tarama_gunu.empty:
            prev = df_ana_veri[df_ana_veri["tarih"] < tarama_tarihi]["tarih"].max()
            if pd.notna(prev):
                fn_logger.info(
                    f"{tarama_tarihi.strftime('%d.%m.%Y')} yok → {prev.strftime('%d.%m.%Y')} kullanıldı"
                )
                df_tarama_gunu = df_ana_veri[df_ana_veri["tarih"] == prev].copy()
                tarama_tarihi = prev
            else:
                fn_logger.warning(
                    f"Belirtilen tarama tarihi ({tarama_tarihi.strftime('%d.%m.%Y')}) ve öncesi için veri yok."
                )
                return {}, {
                    "TUM_FILTRELER_ATLADI": f'Tarama tarihinde ({tarama_tarihi.strftime("%d.%m.%Y")}) ve önceki günlerde veri yok.'
                }
    except Exception as e_tarih_hazirlik:
        fn_logger.error(
            f"Filtreleme için tarama günü verisi hazırlanırken hata: {e_tarih_hazirlik}",
            exc_info=True,
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": f"Tarama günü verisi hazırlama hatası: {e_tarih_hazirlik}"
        }

    if df_tarama_gunu.empty:
        fn_logger.warning(
            f"Belirtilen tarama tarihi ({tarama_tarihi.strftime('%d.%m.%Y')}) için ana veride hiç kayıt bulunamadı."
        )
        return {}, {
            "TUM_FILTRELER_ATLADI": f'Tarama tarihinde ({tarama_tarihi.strftime("%d.%m.%Y")}) veri yok.'
        }

    fn_logger.info(
        f"Tarama gününe ({tarama_tarihi.strftime('%d.%m.%Y')}) ait {len(df_tarama_gunu)} hisse satırı (benzersiz hisse sayısı: {df_tarama_gunu['hisse_kodu'].nunique()}) üzerinde filtreler uygulanacak."
    )
    fn_logger.debug(
        f"Tarama günü DataFrame sütunları (ilk 10): {df_tarama_gunu.columns.tolist()[:10]}"
    )

    filtre_sonuclar: dict[str, dict] = {}
    # Log dictionary containing skipped filters and error details.
    atlanmis_filtreler_log_dict: dict[str, Any] = {}
    kontrol_log: list[dict] = []

    def kaydet_hata(kod, error_type, msg, eksik=None):
        hack = {
            "filtre_kod": kod,
            "hata_tipi": error_type,
            "eksik_ad": eksik or "",
            "detay": msg,
            "cozum_onerisi": _build_solution(error_type, msg if msg else ""),
        }
        atlanmis_filtreler_log_dict.setdefault("hatalar", []).append(hack)

    for index, row in df_filtre_kurallari.iterrows():
        filtre_kodu = row.get("FilterCode")
        python_sorgusu_raw = row.get("PythonQuery")

        if pd.isna(python_sorgusu_raw) or not str(python_sorgusu_raw).strip():
            fn_logger.warning(
                f"Filtre '{filtre_kodu}': Python sorgusu boş veya NaN, atlanıyor."
            )
            msg = "Python sorgusu boş veya NaN."
            atlanmis_filtreler_log_dict[filtre_kodu] = msg
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "GENERIC",
                "hisse_sayisi": 0,
            }
            kaydet_hata(filtre_kodu, "GENERIC", msg)
            continue

        python_sorgusu = str(python_sorgusu_raw)
        sorgu_strip = python_sorgusu.strip()
        if re.search(r"\b(?:and|or)\s*$", sorgu_strip) or sorgu_strip.endswith(
            (">", "<", "=", "(", "&", "|")
        ):
            hata_mesaji = (
                f"Sorgu olası eksik ifade ile bitiyor, atlandı: '{python_sorgusu}'"
            )
            fn_logger.error(f"Filtre '{filtre_kodu}': {hata_mesaji}")
            atlanmis_filtreler_log_dict[filtre_kodu] = hata_mesaji
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }
            kaydet_hata(filtre_kodu, "QUERY_ERROR", hata_mesaji)
            continue
        kullanilan_sutunlar = _extract_columns_from_query(python_sorgusu)
        if "volume_tl" in kullanilan_sutunlar and {"volume", "close"} <= set(
            df_tarama_gunu.columns
        ):
            df_tarama_gunu["volume_tl"] = (
                df_tarama_gunu["volume"] * df_tarama_gunu["close"]
            )
        if {
            "psar_long",
            "psar_short",
        } <= set(df_tarama_gunu.columns) and "psar" in kullanilan_sutunlar:
            df_tarama_gunu["psar"] = df_tarama_gunu["psar_long"].fillna(
                df_tarama_gunu["psar_short"]
            )

        try:
            filtrelenmis_df, info = _apply_single_filter(
                df_tarama_gunu, filtre_kodu, python_sorgusu
            )
        except QueryError as qe:
            msg = str(qe)
            atlanmis_filtreler_log_dict.setdefault("hatalar", []).append(
                {
                    "filtre_kod": filtre_kodu,
                    "hata_tipi": "QUERY_ERROR",
                    "detay": msg,
                    "cozum_onerisi": _build_solution("QUERY_ERROR", msg),
                }
            )
            fn_logger.warning(f"QUERY_ERROR: {filtre_kodu} – {msg}")
            try:
                from utils.error_map import get_reason_hint
                from utils.failure_tracker import log_failure

                reason, hint = get_reason_hint(qe)
                log_failure("filters", filtre_kodu, reason, hint)
            except Exception:
                pass
            continue
        except MissingColumnError as me:
            msg = str(me)
            atlanmis_filtreler_log_dict.setdefault("hatalar", []).append(
                {
                    "filtre_kod": filtre_kodu,
                    "hata_tipi": "GENERIC",
                    "eksik_ad": me.missing,
                    "detay": msg,
                    "cozum_onerisi": _build_solution("GENERIC", msg),
                }
            )
            fn_logger.warning(f"GENERIC: {filtre_kodu} – {msg}")
            try:
                from utils.error_map import get_reason_hint
                from utils.failure_tracker import log_failure

                reason, hint = get_reason_hint(me)
                log_failure("filters", filtre_kodu, reason, hint)
            except Exception:
                pass
            continue

        kontrol_log.append(info)

        if info["durum"] == "CALISTIRILAMADI":
            msg = f"Eksik sütunlar: {info['eksik_sutunlar']}"
            atlanmis_filtreler_log_dict[filtre_kodu] = msg
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }
            kaydet_hata(
                filtre_kodu,
                "QUERY_ERROR",
                msg,
                eksik=info.get("eksik_sutunlar"),
            )
            continue
        if info["durum"] == "HATA":
            msg = info["sebep"]
            atlanmis_filtreler_log_dict[filtre_kodu] = msg
            filtre_sonuclar[filtre_kodu] = {
                "hisseler": [],
                "sebep": "QUERY_ERROR",
                "hisse_sayisi": 0,
            }
            kaydet_hata(filtre_kodu, "QUERY_ERROR", msg)
            continue

        hisse_kodlari_listesi = []
        if filtrelenmis_df is not None and not filtrelenmis_df.empty:
            hisse_kodlari_listesi = filtrelenmis_df["hisse_kodu"].unique().tolist()
        if info["durum"] == "OK":
            sebep_kodu = "OK"
        elif info["durum"] == "DATASIZ":
            sebep_kodu = "GENERIC"
        else:
            sebep_kodu = "NO_STOCK"
        filtre_sonuclar[filtre_kodu] = {
            "hisseler": hisse_kodlari_listesi,
            "sebep": sebep_kodu,
            "hisse_sayisi": len(hisse_kodlari_listesi),
        }
        if sebep_kodu in {"QUERY_ERROR", "GENERIC"}:
            kaydet_hata(filtre_kodu, sebep_kodu, info.get("sebep", ""))

    fn_logger.info(
        f"Tüm filtreler uygulandı. {len(filtre_sonuclar)} filtre için sonuç listesi üretildi."
    )
    if atlanmis_filtreler_log_dict:
        fn_logger.warning(
            f"Atlanan/hatalı filtre sayısı: {len(atlanmis_filtreler_log_dict)}. Detaylar için bir sonraki log seviyesine bakınız veya raporu inceleyiniz."
        )
        for fk, err_msg in atlanmis_filtreler_log_dict.items():
            fn_logger.debug(f"  Atlanan/Hatalı Filtre '{fk}': {err_msg}")

    return filtre_sonuclar, atlanmis_filtreler_log_dict
