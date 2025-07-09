"""Lightweight helper for exporting DataFrames to Excel."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ReportWriter:
    """Write DataFrames to Excel creating parent directories as needed."""

    def write_report(self, df: pd.DataFrame, output_path: Path | str) -> None:
        """Write ``df`` to ``output_path`` in Excel format.

        Parent directories are created automatically before invoking
        :meth:`pandas.DataFrame.to_excel`.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
