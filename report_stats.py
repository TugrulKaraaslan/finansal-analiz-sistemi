"""Dataframe helpers for backtest result statistics and charts."""

from __future__ import annotations

import warnings

import pandas as pd

from filtre_dogrulama import SEBEP_KODLARI
from finansal_analiz_sistemi import config
from utils.pandas_option_safe import option_context


def _get_plotly():
    """Import plotly lazily and return the graphing modules.

    Returns
    -------
    tuple
        Pair of :mod:`plotly.graph_objects` and :func:`plotly.subplots.make_subplots`.
    """
    try:
        import plotly.graph_objects as go_mod
        from plotly.subplots import make_subplots as make_subplots_mod
    except ModuleNotFoundError as exc:  # pragma: no cover - import error path
        raise ModuleNotFoundError("plotly is required for plotting functions") from exc
    return go_mod, make_subplots_mod


WARN_MSG = "".join(
    [
        "The behavior of array concatenation with empty entries is ",
        "deprecated",
    ]
)

warnings.filterwarnings(
    "ignore",
    message=WARN_MSG,
    category=FutureWarning,
    module="report_stats",
)
warnings.filterwarnings(
    "ignore",
    message="Downcasting object dtype arrays on .fillna",
    category=FutureWarning,
    module="report_stats",
)


def _normalize_pct_values(series: pd.Series, *, threshold: float) -> pd.Series:
    """Return numeric percentages scaled when above ``threshold``."""
    s = pd.to_numeric(series, errors="coerce").copy()
    mask = s.abs() > threshold
    s.loc[mask] = s.loc[mask] / 100
    return s.round(2)


def _normalize_pct(s: pd.Series) -> pd.Series:
    """Convert whole-number percentages to fractional scale (÷100 once)."""
    return _normalize_pct_values(s, threshold=1.5)


def build_detay_df(
    summary_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    strateji: str | None = None,
) -> pd.DataFrame:
    """Return detail records enriched with strategy and reason codes.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary data containing ``sebep_kodu`` columns.
    detail_df : pd.DataFrame
        Raw detail DataFrame listing tickers per filter.
    strateji : str, optional
        Strategy name inserted into the output.

    Returns
    -------
    pd.DataFrame
        Normalized detail table ready for Excel export.
    """
    strateji = strateji or getattr(config, "UYGULANAN_STRATEJI", "")
    if "filtre_kodu" not in detail_df.columns:
        merged = pd.DataFrame(
            columns=[
                "filtre_kodu",
                "hisse_kodu",
                "getiri_%",
                "basari",
                "strateji",
                "sebep_kodu",
            ]
        )
    else:
        detail_df = detail_df.drop(columns=["sebep_kodu"], errors="ignore")
        merged = detail_df.merge(
            summary_df[["filtre_kodu", "sebep_kodu"]],
            on="filtre_kodu",
            how="left",
        )
    merged["strateji"] = strateji
    if "getiri_yuzde" in merged.columns:
        merged.rename(columns={"getiri_yuzde": "getiri_%"}, inplace=True)
    if "getiri_%" in merged.columns:
        merged["getiri_%"] = _normalize_pct(merged["getiri_%"]).round(2)
    return merged[
        [
            "filtre_kodu",
            "hisse_kodu",
            "getiri_%",
            "basari",
            "strateji",
            "sebep_kodu",
        ]
    ]


def build_ozet_df(
    summary_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    tarama_tarihi: str = "",
    satis_tarihi: str = "",
) -> pd.DataFrame:
    """Return a normalized summary DataFrame for reporting.

    The raw summary and detail tables produced by the backtest are
    merged together and annotated with reason explanations as well as
    scan and sell dates.
    """
    if summary_df is None:
        summary_df = pd.DataFrame()
    if detail_df is None:
        detail_df = pd.DataFrame()

    col = None
    if "getiri_yuzde" in detail_df.columns:
        col = "getiri_yuzde"
    elif "getiri_%" in detail_df.columns:
        col = "getiri_%"

    if col is not None:
        stats = (
            detail_df.dropna(subset=[col])
            .rename(columns={col: "getiri_yuzde"})
            .groupby("filtre_kodu")["getiri_yuzde"]
            .agg(hisse_sayisi="count", en_yuksek="max", en_dusuk="min")
        )
    else:
        stats = pd.DataFrame(
            columns=[
                "filtre_kodu",
                "hisse_sayisi",
                "en_yuksek",
                "en_dusuk",
                "islemli",
            ]
        )
    stats["islemli"] = stats["hisse_sayisi"].apply(
        lambda x: "EVET" if x > 0 else "HAYIR"
    )

    if not stats.empty:
        summary_df = summary_df.drop(
            columns=["hisse_sayisi", "en_yuksek_%", "en_dusuk_%", "islemli"],
            errors="ignore",
        )
    df = summary_df.merge(
        stats,
        on="filtre_kodu",
        how="left",
        suffixes=("", "_y"),
    )
    for col in ["hisse_sayisi", "en_yuksek", "en_dusuk", "islemli"]:
        if f"{col}_y" in df.columns:
            left = df.get(f"{col}_y", pd.Series(dtype=df[col].dtype)).dropna()
            right = df[col].dropna()
            if not left.empty:
                df[col] = left.combine_first(right)
            df.drop(columns=[f"{col}_y"], inplace=True)
    df["sebep_aciklama"] = df["sebep_kodu"].map(SEBEP_KODLARI).fillna("")
    df["tarama_tarihi"] = tarama_tarihi
    df["satis_tarihi"] = satis_tarihi
    df.rename(
        columns={
            "ort_getiri_%": "ort_getiri_%",
            "en_yuksek": "en_yuksek_%",
            "en_dusuk": "en_dusuk_%",
        },
        inplace=True,
    )
    # Normalize percentage columns to ``0-1`` scale when necessary
    pct_cols_idx = [i for i, c in enumerate(df.columns) if c.endswith("_%")]
    for i in pct_cols_idx:
        df.iloc[:, i] = normalize_pct(df.iloc[:, i])

    subset = df[
        [
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
    ]
    from utils.compat import safe_infer_objects

    with option_context("future.no_silent_downcasting", True):
        subset = safe_infer_objects(subset.fillna({"hisse_sayisi": 0}), copy=False)
    return subset


def build_stats_df(ozet_df: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregated performance statistics."""
    toplam = len(ozet_df)
    islemli = int((ozet_df["islemli"] == "EVET").sum())
    islemsiz = int((ozet_df["islemli"] == "HAYIR").sum())
    hatali = int(
        ozet_df["sebep_kodu"]
        .isin(
            [
                "MISSING_COL",
                "QUERY_ERROR",
            ]
        )
        .sum()
    )
    genel_basari = round(100 * islemli / toplam, 2) if toplam else 0.0
    genel_ortalama = (
        round(
            pd.to_numeric(ozet_df["ort_getiri_%"], errors="coerce").mean(),
            2,
        )
        if toplam
        else 0.0
    )
    return pd.DataFrame(
        [
            {
                "toplam_filtre": toplam,
                "islemli": islemli,
                "işlemsiz": islemsiz,
                "hatalı": hatali,
                "genel_başarı_%": genel_basari,
                "genel_ortalama_%": genel_ortalama,
            }
        ]
    )


# --- Helper: normalize_pct ---
def normalize_pct(series):
    """Return numeric percentages scaled to a fractional range.

    The ``%`` sign is removed first and the remaining string is converted
    to ``float``. Values greater than ``100`` are divided by ``100`` so the
    result is always on a ``0-1`` scale.
    """
    cleaned = series.astype(str).str.replace("%", "", regex=False)
    return _normalize_pct_values(cleaned, threshold=100.0)


def plot_summary_stats(
    ozet_df: pd.DataFrame, detail_df: pd.DataFrame, std_threshold: float = 5.0
):
    """Create four-bar charts summarizing performance using plotly."""
    go, make_subplots = _get_plotly()
    counts = build_stats_df(ozet_df).iloc[0]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Toplam/İşlemli/İşlemsiz/Hatalı",
            "En İyi 10 Ortalama Getiri",
            "En Kötü 10 Ortalama Getiri",
            "En Güvenilir 10 Filtre",
        ),
    )

    fig.add_trace(
        go.Bar(
            x=["toplam", "işlemli", "işlemsiz", "hatalı"],
            y=[
                counts["toplam_filtre"],
                counts["islemli"],
                counts["işlemsiz"],
                counts["hatalı"],
            ],
        ),
        row=1,
        col=1,
    )

    best = ozet_df.sort_values("ort_getiri_%", ascending=False).head(10)
    fig.add_trace(
        go.Bar(x=best["filtre_kodu"], y=best["ort_getiri_%"]),
        row=1,
        col=2,
    )
    worst = ozet_df.sort_values("ort_getiri_%").head(10)
    fig.add_trace(
        go.Bar(x=worst["filtre_kodu"], y=worst["ort_getiri_%"]),
        row=2,
        col=1,
    )
    col = None
    if "getiri_yuzde" in detail_df.columns:
        col = "getiri_yuzde"
    elif "getiri_%" in detail_df.columns:
        col = "getiri_%"
    if col is None:
        raise KeyError("detail_df must contain 'getiri_yuzde' or 'getiri_%'")

    rel_df = (
        detail_df.groupby("filtre_kodu")[col]
        .agg(["count", "std", "mean"])
        .rename(columns={"count": "hisse_sayisi"})
    )
    rel_df = rel_df[rel_df["hisse_sayisi"] >= 3]
    rel_df = rel_df[rel_df["std"] < std_threshold]
    rel_df = rel_df.merge(
        ozet_df[["filtre_kodu", "ort_getiri_%"]],
        left_index=True,
        right_on="filtre_kodu",
        how="left",
    )
    rel_df.sort_values("ort_getiri_%", ascending=False, inplace=True)
    rel_top = rel_df.head(10)
    fig.add_trace(
        go.Bar(x=rel_top["filtre_kodu"], y=rel_top["ort_getiri_%"]),
        row=2,
        col=2,
    )

    fig.update_layout(height=700, showlegend=False)
    return fig
