import pandas as pd
import pytest

from finansal_analiz_sistemi.data_loader import yukle_filtre_dosyasi

pytest.importorskip("pyarrow")

# regression test for new loader formats


def test_excel_and_parquet(tmp_path):
    df = pd.DataFrame({"filtre_kodu": ["F1"], "notlar": [""]})
    xlsx = tmp_path / "f.xlsx"
    df.to_excel(xlsx, index=False)
    assert yukle_filtre_dosyasi(xlsx).equals(df)

    pq = tmp_path / "f.parquet"
    df.to_parquet(pq)
    assert yukle_filtre_dosyasi(pq).equals(df)
