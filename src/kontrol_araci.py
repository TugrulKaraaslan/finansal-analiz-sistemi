"""Sağlık taraması için yardımcı fonksiyonlar.

Tanımlanan her filtre bir kez çalıştırılarak durum bilgileri ve olası
hatalar toplanır. Sonuçlar raporlama aşamasında kullanılır.
"""

import pandas as pd

# Column order used by ``tarama_denetimi`` outputs.
EXPECTED_COLUMNS: tuple[str, ...] = (
    "kod",
    "tip",
    "durum",
    "sebep",
    "eksik_sutunlar",
    "nan_sutunlar",
    "secim_adedi",
)

try:
    from .filter_engine import _apply_single_filter
except ImportError:  # pragma: no cover - fallback when run as script
    from filter_engine import _apply_single_filter


def tarama_denetimi(
    df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame
) -> pd.DataFrame:
    """Filtreleri çalıştırıp özet bilgi döndür.

    Args:
        df_filtreler (pd.DataFrame): Filter definitions with ``kod`` and
            ``PythonQuery`` columns.
        df_indikator (pd.DataFrame): Indicator dataset used by the filters.

    Returns:
        pd.DataFrame: Summary table with columns ``kod``, ``tip``, ``durum``,
        ``sebep``, ``eksik_sutunlar``, ``nan_sutunlar`` and ``secim_adedi``.

    """
    if "kod" not in df_filtreler.columns:
        df_filtreler = df_filtreler.rename(
            columns={"FilterCode": "kod"}, errors="ignore"
        )

    if df_filtreler.empty:
        return pd.DataFrame(
            [
                {
                    "kod": "_SUMMARY",
                    "tip": "tarama",
                    "durum": "NO_ISSUE",
                    "sebep": "",
                    "eksik_sutunlar": "",
                    "nan_sutunlar": "",
                    "secim_adedi": 0,
                }
            ],
            columns=EXPECTED_COLUMNS,
        )

    records = [
        _apply_single_filter(df_indikator, r["kod"], r["PythonQuery"])[1]
        for r in df_filtreler.to_dict("records")
    ]
    summary_df = pd.DataFrame(records)
    if summary_df.empty:
        summary_df = pd.DataFrame(columns=EXPECTED_COLUMNS)  # pragma: no cover
    if not (summary_df["durum"] != "OK").any():
        summary_df = pd.concat(
            [
                summary_df,
                pd.DataFrame(
                    [
                        {
                            "kod": "_SUMMARY",
                            "tip": "tarama",
                            "durum": "NO_ISSUE",
                            "sebep": "",
                            "eksik_sutunlar": "",
                            "nan_sutunlar": "",
                            "secim_adedi": 0,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return summary_df
