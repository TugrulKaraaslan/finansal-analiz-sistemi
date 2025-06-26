from pathlib import Path

import pandas as pd

from finansal_analiz_sistemi.report_utils import save_df_safe


class ReportWriter:
    """Simple Excel writer utility."""

    def write_report(self, df: pd.DataFrame, output_path: Path) -> None:
        """Write DataFrame to Excel creating parent directories if needed."""
        save_df_safe(df, output_path, "summary")
