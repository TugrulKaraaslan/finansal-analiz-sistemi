import pandas as pd
from typing import List


def safe_concat(frames: List[pd.DataFrame], **kwargs) -> pd.DataFrame:
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, **kwargs) if frames else pd.DataFrame()


def safe_to_excel(df: pd.DataFrame, wr, *, sheet_name: str, **kwargs) -> None:
    df.to_excel(excel_writer=wr, sheet_name=sheet_name, **kwargs)
