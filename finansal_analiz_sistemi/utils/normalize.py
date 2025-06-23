import pandas as pd


def normalize_filtre_kodu(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrame içinde 'FilterCode' / 'filtercode' gibi varyasyonları
    tek standarda ('filtre_kodu') indirger.
    Eksikse anlaşılır bir hata yükseltir.
    """
    if "filtre_kodu" in df.columns:
        return df
    aliases = [c for c in df.columns if c.lower() == "filtercode"]
    if aliases:
        return df.rename(columns={aliases[0]: "filtre_kodu"})
    raise KeyError("'filtre_kodu' sütunu bulunamadı – CSV başlıklarını kontrol et")
