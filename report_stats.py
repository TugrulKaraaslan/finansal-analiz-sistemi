import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from filtre_dogrulama import SEBEP_KODLARI
import config


def build_ozet_df(summary_df: pd.DataFrame, detail_df: pd.DataFrame,
                  tarama_tarihi: str = "", satis_tarihi: str = "") -> pd.DataFrame:
    """Build summary dataframe combining backtest results and details."""
    if summary_df is None:
        summary_df = pd.DataFrame()
    if detail_df is None:
        detail_df = pd.DataFrame()

    stats = (
        detail_df.dropna(subset=["getiri_yuzde"])
        .groupby("filtre_kodu")["getiri_yuzde"]
        .agg(hisse_sayisi="count", en_yuksek="max", en_dusuk="min")
    )
    stats["islemli"] = stats["hisse_sayisi"].apply(lambda x: "EVET" if x > 0 else "HAYIR")

    df = summary_df.merge(stats, on="filtre_kodu", how="left")
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
    return df[[
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
    ]].fillna({"hisse_sayisi": 0})


def build_detay_df(summary_df: pd.DataFrame, detail_df: pd.DataFrame,
                   strateji: str | None = None) -> pd.DataFrame:
    """Add strategy and reason code info to detail dataframe."""
    strateji = strateji or getattr(config, "UYGULANAN_STRATEJI", "")
    merged = detail_df.merge(summary_df[["filtre_kodu", "sebep_kodu"]], on="filtre_kodu", how="left")
    merged["strateji"] = strateji
    merged.rename(columns={"getiri_yuzde": "getiri_%"}, inplace=True)
    return merged[[
        "filtre_kodu",
        "hisse_kodu",
        "getiri_%",
        "basari",
        "strateji",
        "sebep_kodu",
    ]]


def build_stats_df(ozet_df: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregated performance statistics."""
    toplam = len(ozet_df)
    islemli = int((ozet_df["islemli"] == "EVET").sum())
    islemesiz = int((ozet_df["islemli"] == "HAYIR").sum())
    hatali = int(ozet_df["sebep_kodu"].isin(["MISSING_COL", "QUERY_ERROR"]).sum())
    genel_basari = round(100 * islemli / toplam, 2) if toplam else 0.0
    genel_ortalama = round(pd.to_numeric(ozet_df["ort_getiri_%"], errors="coerce").mean(), 2) if toplam else 0.0
    return pd.DataFrame([
        {
            "toplam_filtre": toplam,
            "islemli": islemli,
            "işlemsiz": islemesiz,
            "hatalı": hatali,
            "genel_başarı_%": genel_basari,
            "genel_ortalama_%": genel_ortalama,
        }
    ])


def plot_summary_stats(ozet_df: pd.DataFrame, detail_df: pd.DataFrame,
                       std_threshold: float = 5.0):
    """Create four-bar charts summarizing performance using plotly."""
    counts = build_stats_df(ozet_df).iloc[0]

    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Toplam/İşlemli/İşlemsiz/Hatalı",
        "En İyi 10 Ortalama Getiri",
        "En Kötü 10 Ortalama Getiri",
        "En Güvenilir 10 Filtre",
    ))

    # Bar 1
    fig.add_trace(go.Bar(x=["toplam", "işlemli", "işlemsiz", "hatalı"],
                         y=[counts["toplam_filtre"], counts["islemli"], counts["işlemsiz"], counts["hatalı"]]),
                  row=1, col=1)

    # Bar 2 - best
    best = ozet_df.sort_values("ort_getiri_%", ascending=False).head(10)
    fig.add_trace(go.Bar(x=best["filtre_kodu"], y=best["ort_getiri_%"]), row=1, col=2)

    # Bar 3 - worst
    worst = ozet_df.sort_values("ort_getiri_%").head(10)
    fig.add_trace(go.Bar(x=worst["filtre_kodu"], y=worst["ort_getiri_%"]), row=2, col=1)

    # Bar 4 - reliability
    rel_df = (
        detail_df.groupby("filtre_kodu")["getiri_yuzde"].agg(["count", "std", "mean"]).rename(columns={"count": "hisse_sayisi"})
    )
    rel_df = rel_df[rel_df["hisse_sayisi"] >= 3]
    rel_df = rel_df[rel_df["std"] < std_threshold]
    rel_df = rel_df.merge(ozet_df[["filtre_kodu", "ort_getiri_%"]], left_index=True, right_on="filtre_kodu", how="left")
    rel_df.sort_values("ort_getiri_%", ascending=False, inplace=True)
    rel_top = rel_df.head(10)
    fig.add_trace(go.Bar(x=rel_top["filtre_kodu"], y=rel_top["ort_getiri_%"]), row=2, col=2)

    fig.update_layout(height=700, showlegend=False)
    return fig
