import pandas as pd
from finansal_analiz_sistemi.utils.normalize import normalize_filtre_kodu


def load_error_list(csv_path: str) -> pd.DataFrame:
    """Load error list CSV and normalize column names."""
    df = normalize_filtre_kodu(pd.read_csv(csv_path, sep=";"))
    return df
