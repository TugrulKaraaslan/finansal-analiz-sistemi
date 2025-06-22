from pathlib import Path

import pandas as pd


class ReportWriter:
    """Simple Excel writer utility."""

    def write_report(self, df: pd.DataFrame, output_path: Path) -> None:
        """Write DataFrame to Excel creating parent directories if needed."""
        # Ebeveyn klasörleri otomatik oluştur
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
