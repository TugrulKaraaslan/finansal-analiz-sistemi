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

    def write_report(self, df: pd.DataFrame, output_path: Path | str) -> Path:
        """Write ``df`` to ``output_path`` and return the destination."""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
        return output_path
