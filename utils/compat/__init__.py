"""
Compatibility layer around select ``pandas`` helpers.

These shims smooth over API differences between ``pandas`` releases so
the rest of the codebase can remain version agnostic.
"""

import logging
from itertools import chain
from typing import Iterable, Optional

import pandas as pd
from packaging import version as _v

__all__ = ["safe_concat", "safe_infer_objects", "safe_to_excel"]

_PANDAS_HAS_COPY = _v.parse(pd.__version__) >= _v.parse("2.0.0")


def safe_concat(frames: Iterable[Optional[pd.DataFrame]], **kwargs) -> pd.DataFrame:
    """Concatenate ``frames`` while skipping ``None`` and empty inputs.

    Parameters
    ----------
    frames : Iterable[Optional[pandas.DataFrame]]
        Sequence of DataFrames to concatenate. ``None`` values are ignored.
        Empty frames are skipped unless all inputs are empty.
    **kwargs : Any
        Additional arguments forwarded to :func:`pandas.concat`.

    Returns
    -------
    pandas.DataFrame
        Concatenated frame or an empty frame when ``frames`` yields no rows.
    """
    valid_iter = (f for f in frames if isinstance(f, pd.DataFrame) and not f.empty)
    first = next(valid_iter, None)
    if first is None:
        return pd.DataFrame()
    return pd.concat(chain([first], valid_iter), **kwargs)


def safe_infer_objects(df: pd.DataFrame, *, copy: bool = False) -> pd.DataFrame:
    """Compatibility wrapper for ``infer_objects`` with copy parameter.

    Args:
        df (pd.DataFrame): DataFrame to operate on.
        copy (bool, optional): Whether to return a copy. Defaults to ``False``.

    Returns:
        pd.DataFrame: Result of ``infer_objects``.
    """
    if _PANDAS_HAS_COPY:
        return df.infer_objects(copy=copy)
    res = df.infer_objects()
    return res.copy() if copy else res


def safe_to_excel(
    df: pd.DataFrame, wr: pd.ExcelWriter, *, sheet_name: str, **kwargs
) -> None:
    """Write ``df`` to ``wr`` using ``sheet_name``.

    Logs a warning when ``df`` is empty to help callers detect accidental
    omissions. The helper simply forwards ``**kwargs`` to
    :meth:`pandas.DataFrame.to_excel`.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to write.
    wr : pandas.ExcelWriter
        Writer instance returned by :class:`pandas.ExcelWriter`.
    sheet_name : str
        Target worksheet name.
    **kwargs : Any
        Additional arguments forwarded to ``to_excel``.
    """
    if df.empty:
        logging.getLogger(__name__).warning(
            "Excel sheet '%s' boş – yine de yazılıyor", sheet_name
        )
    df.to_excel(excel_writer=wr, sheet_name=sheet_name, **kwargs)
