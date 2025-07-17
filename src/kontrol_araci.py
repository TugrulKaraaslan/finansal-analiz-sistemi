"""Diagnostic runner for filter definitions.

Each filter is executed once to collect status flags and error details
used in reporting.
"""

import pandas as pd

EXPECTED_COLUMNS = [
    "kod",
    "tip",
    "durum",
    "sebep",
    "eksik_sutunlar",
    "nan_sutunlar",
    "secim_adedi",
]

try:
    from .filter_engine import _apply_single_filter
except ImportError:  # pragma: no cover - fallback when run as script
    from filter_engine import _apply_single_filter


def tarama_denetimi(
    df_filtreler: pd.DataFrame, df_indikator: pd.DataFrame
) -> pd.DataFrame:
    """Run each filter once and collect status information.

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

    records: list[dict] = []
    for row in df_filtreler.itertuples(index=False):
        _, info = _apply_single_filter(
            df_indikator, getattr(row, "kod"), getattr(row, "PythonQuery")
        )
        records.append(info)
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)  # pragma: no cover
    if not (df["durum"] != "OK").any():
        df = pd.concat(
            [
                df,
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
    return df
