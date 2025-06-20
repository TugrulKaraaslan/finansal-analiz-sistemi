import pandas as pd
from typing import List
from packaging import version as _v


def safe_concat(frames: List[pd.DataFrame], **kwargs) -> pd.DataFrame:
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, **kwargs) if frames else pd.DataFrame()


def safe_to_excel(df: pd.DataFrame, wr, *, sheet_name: str, **kwargs) -> None:
    df.to_excel(excel_writer=wr, sheet_name=sheet_name, **kwargs)


_PANDAS_HAS_COPY = _v.parse(pd.__version__) >= _v.parse("2.0.0")


def safe_infer_objects(df: pd.DataFrame, *, copy: bool = False) -> pd.DataFrame:
    """Pandas <2.0 için 'copy' parametresi olmayan uyum katmanı."""
    if _PANDAS_HAS_COPY:
        return df.infer_objects(copy=copy)
    res = df.infer_objects()
    return res.copy() if copy else res
