"""Backward compatible wrappers for pandas utilities."""

import logging
from typing import List

import pandas as pd
from packaging import version as _v

__all__ = ["safe_concat", "safe_to_excel", "safe_infer_objects"]


def safe_concat(frames: List[pd.DataFrame], **kwargs) -> pd.DataFrame:
    """Concatenate non-empty frames or return an empty ``DataFrame``."""
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, **kwargs) if frames else pd.DataFrame()


def safe_to_excel(df: pd.DataFrame, wr, *, sheet_name: str, **kwargs) -> None:
    """Write ``df`` to an Excel writer using keyword-only ``sheet_name``.

    Logs a warning when ``df`` is empty. Compatible with ``pandas>=3``.
    """
    if df.empty:
        logging.getLogger(__name__).warning(
            "Excel sheet '%s' boş – yine de yazılıyor", sheet_name
        )
    df.to_excel(excel_writer=wr, sheet_name=sheet_name, **kwargs)


_PANDAS_HAS_COPY = _v.parse(pd.__version__) >= _v.parse("2.0.0")


def safe_infer_objects(df: pd.DataFrame, *, copy: bool = False) -> pd.DataFrame:
    """Compatibility wrapper for ``infer_objects`` with copy parameter."""
    if _PANDAS_HAS_COPY:
        return df.infer_objects(copy=copy)
    res = df.infer_objects()
    return res.copy() if copy else res
