import tempfile
from pathlib import Path

import pandas as pd
import pytest

from finansal_analiz_sistemi.data_loader import yukle_filtre_dosyasi

pytest.importorskip("pyarrow")


def test_filter_loader_formats():
    df = pd.DataFrame({"filtre_kodu": ["F1"], "notlar": [""]})
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "filter.xlsx"
        df.to_excel(p, index=False)
        assert yukle_filtre_dosyasi(p).equals(df)
        q = Path(td) / "filter.parquet"
        df.to_parquet(q)
        assert yukle_filtre_dosyasi(q).equals(df)
