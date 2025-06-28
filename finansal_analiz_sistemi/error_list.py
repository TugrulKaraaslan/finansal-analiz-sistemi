import pandas as pd

from finansal_analiz_sistemi.utils.normalize import normalize_filtre_kodu


def load_error_list(csv_path: str) -> pd.DataFrame:
    """Load error list CSV and normalize column names.

    Parameters
    ----------
    csv_path : str
        Path to the semicolon separated CSV file. Files produced by Excel may
        contain a UTF-8 BOM, so we read using ``utf-8-sig`` encoding to ensure
        the ``filtre_kodu`` column is detected correctly.
    """

    df = pd.read_csv(csv_path, sep=";", encoding="utf-8-sig")
    return normalize_filtre_kodu(df)
