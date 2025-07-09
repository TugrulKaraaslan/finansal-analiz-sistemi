"""Lightweight Excel reporting utility."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ReportWriter:
    """Simple Excel writer utility."""

    def write_report(self, df: pd.DataFrame, output_path: Path | str) -> None:
        """Export ``df`` to ``output_path`` as an Excel workbook.

        Parent directories are created automatically before calling
        :meth:`pandas.DataFrame.to_excel`.
        """
        output_path = Path(output_path)
        # Create parent directories automatically
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
