import logging
from pathlib import Path

import pandas as pd

from utils.compat import safe_to_excel

logger = logging.getLogger(__name__)


def save_df_safe(
    df: pd.DataFrame, file_path: str | Path, name: str, allow_empty: bool = False
) -> Path:
    """Safely write dataframe to Excel.

    Parameters
    ----------
    df : pd.DataFrame
        Data to write.
    file_path : str or Path
        Target Excel file.
    name : str
        Name used for logging / sheet label.
    allow_empty : bool, optional
        If ``True`` empty dataframes produce an ``EMPTY_REPORT`` sheet instead of
        raising ``ValueError``.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        if not allow_empty:
            logger.error("DataFrame '%s' empty", name)
            raise ValueError("empty dataframe")
        with pd.ExcelWriter(path, engine="openpyxl") as wr:
            safe_to_excel(
                pd.DataFrame({"EMPTY_REPORT": []}),
                wr,
                sheet_name="EMPTY_REPORT",
                index=False,
            )
        logger.warning("Placeholder EMPTY_REPORT written to %s", path)
    else:
        with pd.ExcelWriter(path, engine="openpyxl") as wr:
            safe_to_excel(df, wr, sheet_name=name, index=False)
        logger.info("Saved %s with %d rows → %s", name, len(df), path)
    return path
