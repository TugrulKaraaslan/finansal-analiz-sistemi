"""Lightweight helper for exporting DataFrames to Excel.

The :class:`ReportWriter` ensures the output directory exists before the
workbook is written.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ReportWriter:
    """Write DataFrames to Excel while ensuring the destination exists.

    Parent directories are created automatically before calling
    :meth:`pandas.DataFrame.to_excel`.
    """

    def write_report(self, df: pd.DataFrame, output_path: Path | str) -> None:
        """Write ``df`` to an Excel file.

        Creates missing parent directories before calling
        :meth:`pandas.DataFrame.to_excel`.

        Args:
            df (pd.DataFrame): Data to export.
            output_path (Path | str): Target Excel file path.

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
