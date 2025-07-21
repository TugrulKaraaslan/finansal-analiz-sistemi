"""
Utilities for loading CSV, Excel and Parquet datasets.

These helpers return ``pandas`` DataFrames while caching reads to
minimize disk access.
"""

from __future__ import annotations

import glob
import logging
import os
from functools import lru_cache, partial
from pathlib import Path
from typing import Optional

import pandas as pd

from data_loader_cache import DataLoaderCache
from finansal_analiz_sistemi import config
from finansal_analiz_sistemi.logging_config import get_logger
from utils.compat import safe_concat

COLS = ["tarih", "filtre_kodu", "PythonQuery"]

logger = get_logger(__name__)

_cache_loader = DataLoaderCache(logger=logger)

_read_excel = partial(pd.read_excel, engine="openpyxl")


@lru_cache(maxsize=None)
def _read_excel_cached_normalized(path: str) -> pd.DataFrame:
    """Read ``path`` with ``openpyxl`` and cache the result."""

    return _read_excel(path)


def _read_excel_cached(path: str | Path) -> pd.DataFrame:
    """Return an Excel file read via ``openpyxl`` with caching.

    ``path`` values are normalized to strings so ``Path`` objects and
    string arguments share the same cache entry.

    Parameters
    ----------
    path : str | pathlib.Path
        Dosya yolu.

    Returns
    -------
    pandas.DataFrame
        Okunan Excel içeriği.
    """

    return _read_excel_cached_normalized(str(path))


DATE_COLUMN_CANDIDATES = (
    "Tarih",
    "tarih",
    "TARİH",
    "Date",
    "date",
    "Zaman",
    "zaman",
)


def _find_date_column(df: pd.DataFrame) -> str | None:
    """Return the first column containing date-like values.

    Standard column names defined in :data:`DATE_COLUMN_CANDIDATES` are
    considered first. Any column that starts with ``"Unnamed:"`` is also
    inspected so exported index columns can be detected. The helper only
    returns a candidate when at least one value can be parsed as a date.
    """

    candidates = list(DATE_COLUMN_CANDIDATES)
    candidates.extend(c for c in df.columns if str(c).startswith("Unnamed:"))

    for col in candidates:
        if col not in df.columns:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            return col
        if pd.to_datetime(series, errors="coerce", dayfirst=True).notna().any():
            return col
    return None


def _standardize_date_column(
    df: pd.DataFrame,
    file_path_for_log: str = "",
    logger_param: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Rename the first matching date column to ``tarih``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to inspect for a date column.
    file_path_for_log : str, optional
        File path used in log messages.
    logger_param : logging.Logger, optional
        Logger instance used for debug messages.

    Returns
    -------
    pandas.DataFrame
        DataFrame with a standardized date column.
    """
    if logger_param is None:
        logger_param = logger
    log = logger_param

    found_col = _find_date_column(df)
    file_name = os.path.basename(file_path_for_log)

    if found_col and found_col != "tarih":
        df.rename(columns={found_col: "tarih"}, inplace=True)
        log.debug("'%s': Tarih sütunu '%s' -> 'tarih'", file_name, found_col)
    elif not found_col:
        log.warning(
            "'%s': Standart tarih sütunu ('Tarih' vb.) bulunamadı. Mevcut sütunlar: %s",
            file_name,
            df.columns.tolist(),
        )
    return df


def _standardize_ohlcv_columns(
    df: pd.DataFrame,
    file_path_for_log: str = "",
    logger_param: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Normalize OHLCV column names using ``config.OHLCV_MAP``.

    Args:
        df (pd.DataFrame): DataFrame with potential OHLCV columns.
        file_path_for_log (str, optional): File path used in log messages.
        logger_param (logging.Logger, optional): Logger instance.

    Returns:
        pd.DataFrame: DataFrame with standardized OHLCV column names.

    """
    if logger_param is None:
        logger_param = logger
    log = logger_param
    file_name_short = os.path.basename(file_path_for_log)  # Short file name for logging
    log.debug(f"--- '{file_name_short}': OHLCV Standardizasyonu Başlıyor ---")
    log.debug(f"'{file_name_short}': Orijinal Sütunlar: {df.columns.tolist()}")

    rename_map: dict[str, str] = {}
    existing = set(df.columns)

    for raw_name, standard_name in config.OHLCV_MAP.items():
        if (
            raw_name in existing
            and raw_name != standard_name
            and standard_name not in existing
            and standard_name not in rename_map.values()
        ):
            rename_map[raw_name] = standard_name
            log.debug(
                f"'{file_name_short}': Eşleştirme bulundu: '{raw_name}' -> '{standard_name}'"
            )

    if rename_map:
        log.info(
            f"'{file_name_short}': Uygulanacak yeniden adlandırma haritası: {rename_map}"
        )
        try:
            df.rename(columns=rename_map, inplace=True)
            log.info(
                f"'{file_name_short}': Yeniden adlandırma sonrası sütunlar: {df.columns.tolist()}"
            )
        except Exception as e_rename:
            log.error(
                f"'{file_name_short}': Sütunlar yeniden adlandırılırken HATA: {e_rename}. Harita: {rename_map}",
                exc_info=True,
            )
    else:
        log.debug(
            f"'{file_name_short}': OHLCV için yeniden adlandırılacak sütun bulunamadı "
            "(ya zaten standart ya da MAP'te eşleşme yok)."
        )

    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(df.columns)

    if missing:
        log.warning(
            f"'{file_name_short}': Standartlaştırma sonrası bazı OHLCV sütunları eksik: {sorted(missing)}"
        )
    else:
        log.info(
            f"'{file_name_short}': Tüm temel OHLCV sütunları başarıyla oluşturuldu/bulundu."
        )
    log.debug(f"--- '{file_name_short}': OHLCV Standardizasyonu Tamamlandı ---")
    return df


def check_and_create_dirs(*dir_paths: str | Path) -> list[Path]:
    """Ensure each path in ``dir_paths`` exists as a directory.

    Paths are expanded and resolved to absolute :class:`~pathlib.Path`
    instances. Missing directories are created as needed. Any path that
    already exists as a file triggers an error log entry and is skipped.

    Parameters
    ----------
    *dir_paths : str | pathlib.Path
        One or more directory paths to verify or create.

    Returns
    -------
    list[pathlib.Path]
        A list of directories that were created during the call. Existing
        directories are not included.
    """

    created: list[Path] = []

    for path in dir_paths:
        if not path:
            continue
        p = Path(path).expanduser().resolve(strict=False)
        if p.exists() and not p.is_dir():
            logger.error("Beklenen dizin aslında dosya: %s", p)
            continue
        if not p.exists():
            try:
                p.mkdir(parents=True, exist_ok=True)
                created.append(p)
                logger.info("Dizin oluşturuldu: %s", p)
            except Exception as exc:  # pragma: no cover - I/O errors
                logger.error(
                    "Dizin oluşturulamadı: %s. Hata: %s", p, exc, exc_info=True
                )

    return created


def load_data(path: str) -> pd.DataFrame:
    """Return cached CSV contents as a DataFrame.

    Args:
        path (str): CSV file path.

    Returns:
        pd.DataFrame: DataFrame loaded via :class:`DataLoaderCache`.

    """
    return _cache_loader.load_csv(path)


def load_excel_katalogu(
    path: str, logger_param: Optional[logging.Logger] = None
) -> pd.DataFrame | None:
    """Load an Excel file and optionally write a Parquet copy.

    Args:
        path (str): Excel file path.
        logger_param (logging.Logger, optional): Logger instance.

    Returns:
        pd.DataFrame | None: DataFrame if valid data is found, otherwise ``None``.

    """
    if logger_param is None:
        logger_param = logger
    log = logger_param
    try:
        df = _read_excel_cached(path)
    except Exception as e:
        log.error(f"Excel dosyası ({path}) okunamadı: {e}", exc_info=False)
        return None

    df.columns = df.columns.str.strip().str.lower()
    if len(df) < 252:
        log.debug(f"{path} kısa veri – atlandı")
        return None

    parquet_p = path.replace(".xlsx", ".parquet")
    if not os.path.exists(parquet_p):
        try:
            df.to_parquet(parquet_p)
        except Exception as e:
            log.warning(f"Parquet kaydedilemedi: {parquet_p}: {e}", exc_info=False)
    return df


def load_filter_csv(path: str) -> pd.DataFrame:
    """Load filter CSV and ensure expected columns.

    Legacy files with only ``filtre_kodu`` and ``PythonQuery`` are upgraded
    by inserting a ``tarih`` column.

    Args:
        path (str): CSV file path.

    Returns:
        pd.DataFrame: Loaded DataFrame with standardized columns.

    """
    # Try headerless read first (legacy files have only two columns)
    raw = pd.read_csv(path, sep=";")
    if list(raw.columns) == ["filtre_kodu", "PythonQuery"]:
        raw.insert(0, "tarih", pd.NA)
        raw.columns = COLS
        return raw

    df = pd.read_csv(
        path,
        names=COLS,  # expected column names
        header=None,  # file has no header
        skiprows=1,  # skip initial dummy row
        sep=";",
    )

    # Safety check: fail loudly if columns differ from expectation
    if list(df.columns) != COLS:
        raise ValueError(f"Beklenen kolonlar {COLS}, gelen: {df.columns}")

    return df


def read_prices(path: str | Path, **kwargs) -> pd.DataFrame:
    """Read a price CSV using delimiter auto-detection.

    The first line is inspected to choose ``;`` when semicolons dominate,
    ```,` when commas dominate or ``sep=None`` otherwise.

    Args:
        path (str | Path): CSV file path.
        **kwargs: Additional options passed to :func:`pandas.read_csv`.

    Returns:
        pd.DataFrame: Parsed price data.

    """
    encoding = kwargs.get("encoding", "utf-8")
    with open(path, encoding=encoding) as f:
        first = f.readline().lstrip("#")
    delimiter: str | None
    if first.count(";") > first.count(","):
        delimiter = ";"
    elif "," in first:
        delimiter = ","
    else:
        delimiter = None
    kwargs.setdefault("engine", "python")
    return pd.read_csv(path, sep=delimiter, **kwargs)


def yukle_filtre_dosyasi(
    filtre_dosya_yolu_cfg: str | None = None,
    logger_param: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """Load filter definitions from various formats.

    Args:
        filtre_dosya_yolu_cfg (str | None, optional): Custom file path.
        logger_param (logging.Logger, optional): Logger instance.

    Returns:
        pd.DataFrame: Loaded filter definitions.

    """
    if logger_param is None:
        logger_param = logger
    log = logger_param
    path = Path(filtre_dosya_yolu_cfg or config.FILTRE_DOSYA_YOLU)
    log.info(f"Filtre dosyası yükleniyor: {path}")

    suf = path.suffix.lower()
    if suf in {".xlsx", ".xls"}:
        df = pd.read_excel(path, sheet_name=0, engine="openpyxl", keep_default_na=False)
    elif suf == ".parquet":
        df = pd.read_parquet(path)
    else:
        from finansal_analiz_sistemi.utils.normalize import normalize_filtre_kodu

        df = pd.read_csv(
            path,
            sep=";",
            dtype="string",
            keep_default_na=False,
            na_filter=False,
        )
        df = normalize_filtre_kodu(df)

        # Hâlâ eksikse, erken ve anlaşılır hata ver.
        if "filtre_kodu" not in df.columns:
            raise ValueError(
                f"{path.name}: 'filtre_kodu' sütunu bulunamadı; CSV başlıklarını kontrol et."
            )

    if "filtre_kodu" in df.columns:
        col = df["filtre_kodu"]
        df = df[col.notna() & col.astype(str).str.strip().ne("")]
    for col in ("min", "max"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    log.info(f"Filtre dosyası '{path}' başarıyla yüklendi. {len(df)} filtre bulundu.")
    return df


def yukle_hisse_verileri(
    hisse_dosya_pattern_cfg: str | None = None,
    parquet_ana_dosya_yolu_cfg: str | None = None,
    force_excel_reload: bool = False,
    logger_param: Optional[logging.Logger] = None,
) -> pd.DataFrame | None:
    """Load raw stock data from CSV or Excel sources.

    Args:
        hisse_dosya_pattern_cfg (str | None, optional): Glob pattern for CSV files.
        parquet_ana_dosya_yolu_cfg (str | None, optional): Path to cached Parquet file.
        force_excel_reload (bool, optional): Force re-reading Excel/CSV even if Parquet exists.
        logger_param (logging.Logger, optional): Logger instance.

    Returns:
        pd.DataFrame | None: Combined DataFrame or ``None`` on failure.

    """
    if logger_param is None:
        logger_param = logger
    fn_logger = logger_param
    parquet_dosya_yolu = parquet_ana_dosya_yolu_cfg or config.PARQUET_ANA_DOSYA_YOLU
    hisse_dosya_pattern = hisse_dosya_pattern_cfg or config.HISSE_DOSYA_PATTERN
    veri_klasoru = config.VERI_KLASORU

    check_and_create_dirs(
        veri_klasoru,
        os.path.dirname(parquet_dosya_yolu) if parquet_dosya_yolu else None,
    )

    if (
        not force_excel_reload
        and parquet_dosya_yolu
        and os.path.exists(parquet_dosya_yolu)
    ):
        try:
            df_birlesik = pd.read_parquet(parquet_dosya_yolu)
            fn_logger.info(
                f"Birleşik hisse verileri Parquet dosyasından yüklendi: {parquet_dosya_yolu} "
                f"({len(df_birlesik)} satır)"
            )
            if not df_birlesik.empty and "hisse_kodu" in df_birlesik.columns:
                fn_logger.debug(
                    f"Parquet'ten yüklenen hisse kodları (ilk 5): {df_birlesik['hisse_kodu'].unique()[:5]}"
                )
            return df_birlesik
        except Exception as e:
            fn_logger.warning(
                f"Parquet dosyası ({parquet_dosya_yolu}) okunamadı, Excel/CSV'den yeniden yüklenecek. "
                f"Hata: {e}",
                exc_info=False,
            )

    fn_logger.info(
        "Parquet dosyası bulunamadı/kullanılmadı veya zorla yeniden yükleme aktif. "
        "Kaynak CSV/Excel dosyaları okunacak..."
    )

    excel_dosyalari = glob.glob(os.path.join(veri_klasoru, "*.xlsx")) + glob.glob(
        os.path.join(veri_klasoru, "*.xls")
    )
    csv_dosyalari = glob.glob(hisse_dosya_pattern)

    filtre_dosya_tam_yolu_abs = os.path.abspath(config.FILTRE_DOSYA_YOLU)
    excel_dosyalari = [
        f
        for f in excel_dosyalari
        if os.path.abspath(f) != filtre_dosya_tam_yolu_abs
        and not os.path.basename(f).startswith("~$")
    ]
    csv_dosyalari = [
        f
        for f in csv_dosyalari
        if os.path.abspath(f) != filtre_dosya_tam_yolu_abs
        and not os.path.basename(f).startswith("~$")
    ]

    if not excel_dosyalari and not csv_dosyalari:
        fn_logger.critical(
            f"Belirtilen pattern'de ({hisse_dosya_pattern} ve Excel varyasyonları) kaynak veri dosyası bulunamadı "
            f"({veri_klasoru}). Sistem devam edemez."
        )
        return None

    tum_hisse_datalari = []
    for dosya_yolu in excel_dosyalari:
        hisse_kodu_excel = ""
        try:
            xls = _cache_loader.load_excel(dosya_yolu)
            for sayfa_adi in xls.sheet_names:
                hisse_kodu_excel = str(sayfa_adi).upper().strip()
                df_hisse = xls.parse(sayfa_adi)
                df_hisse = _standardize_date_column(df_hisse, dosya_yolu, fn_logger)
                df_hisse = _standardize_ohlcv_columns(
                    df_hisse, dosya_yolu, fn_logger
                )  # Include file path in logs
                df_hisse["hisse_kodu"] = hisse_kodu_excel
                tum_hisse_datalari.append(df_hisse)
        except Exception as e:
            fn_logger.error(
                f"Excel dosyası ({dosya_yolu} - Sayfa: {hisse_kodu_excel if hisse_kodu_excel else 'BILINMIYOR'}) "
                f"işlenirken hata: {e}",
                exc_info=False,
            )

    for dosya_yolu in csv_dosyalari:
        hisse_kodu_csv = ""
        try:
            base_name = os.path.basename(dosya_yolu)
            hisse_kodu_csv = os.path.splitext(base_name)[0]
            if ".xlsx - " in hisse_kodu_csv:
                hisse_kodu_csv = hisse_kodu_csv.split(".xlsx - ")[-1]

            df_hisse = _cache_loader.load_csv(
                dosya_yolu,
                delimiter=None,
                engine="python",
                encoding="utf-8-sig",
                skipinitialspace=True,
            )
            df_hisse = _standardize_date_column(
                df_hisse, dosya_yolu, fn_logger
            )  # Include file path in logs
            df_hisse = _standardize_ohlcv_columns(
                df_hisse, dosya_yolu, fn_logger
            )  # Include file path in logs
            df_hisse["hisse_kodu"] = str(hisse_kodu_csv).upper().strip()
            tum_hisse_datalari.append(df_hisse)
        except Exception as e:
            fn_logger.error(
                f"CSV dosyası ({dosya_yolu} - Hisse Kodu Tahmini: {hisse_kodu_csv}) işlenirken hata: {e}",
                exc_info=False,
            )

    if not tum_hisse_datalari:
        fn_logger.critical("Hiçbir hisse verisi yüklenemedi. Sistem devam edemez.")
        return None

    try:
        df_birlesik = safe_concat(tum_hisse_datalari, ignore_index=True)
        fn_logger.info(
            f"Toplam {len(df_birlesik)} satır ve {df_birlesik['hisse_kodu'].nunique()} farklı hisse verisi "
            "birleştirildi."
        )
    except Exception as e:
        fn_logger.critical(
            f"Hisse verileri birleştirilirken KRİTİK HATA: {e}. Sistem devam edemez.",
            exc_info=True,
        )
        return None

    # Log combined DataFrame columns once more before writing Parquet
    fn_logger.debug(
        f"Birleştirilmiş DataFrame (Parquet'e yazılmadan önce) sütunları: {df_birlesik.columns.tolist()}"
    )

    if not df_birlesik.empty and parquet_dosya_yolu:
        try:
            gerekli_sutunlar_parquet = [
                "tarih",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "hisse_kodu",
            ]
            eksik_sutunlar_kayit_oncesi = [
                s for s in gerekli_sutunlar_parquet if s not in df_birlesik.columns
            ]
            if eksik_sutunlar_kayit_oncesi:
                fn_logger.warning(
                    f"Parquet'e kaydetmeden önce birleştirilmiş DataFrame'de temel sütunlar eksik: "
                    f"{eksik_sutunlar_kayit_oncesi}. Bu durum sorunlara yol açabilir."
                )
            else:
                fn_logger.debug(
                    "Parquet'e kaydetmeden önce tüm temel sütunlar birleşik DataFrame'de mevcut."
                )

            df_birlesik.to_parquet(parquet_dosya_yolu, index=False)
            fn_logger.info(
                f"Birleşik hisse verileri Parquet olarak kaydedildi: {parquet_dosya_yolu}"
            )
        except Exception as e:
            fn_logger.error(
                f"Parquet dosyası ({parquet_dosya_yolu}) kaydedilemedi: {e}",
                exc_info=False,
            )

    return df_birlesik
