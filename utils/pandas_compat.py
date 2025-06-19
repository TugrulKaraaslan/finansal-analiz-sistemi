import pandas as pd


def safe_to_excel(df, writer, sheet_name: str, **kwargs):
    """Pandas 3.0 uyumlu to_excel (sheet_name keyword-only)."""
    df.to_excel(excel_writer=writer, sheet_name=sheet_name, **kwargs)


def safe_concat(dfs, axis=0, **kwargs):
    """Boş DataFrame'leri eleyerek güvenli pd.concat."""
    dfs = [d for d in dfs if not d.empty]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, axis=axis, **kwargs)
