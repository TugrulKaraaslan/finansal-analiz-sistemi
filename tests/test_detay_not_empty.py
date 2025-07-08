import pandas as pd

from report_generator import _build_detay_df


def test_detay_not_empty():
    """Test test_detay_not_empty."""
    trades = pd.DataFrame(
        {
            "filtre_kodu": ["F1", "F1"],
            "hisse_kodu": ["AAA", "BBB"],
            "getiri_%": [5.0, -2.0],
            "basari": ["BAŞARILI", "BAŞARISIZ"],
            "strateji": ["S", "S"],
            "sebep_kodu": ["OK", "OK"],
        }
    )
    detay_list = [
        pd.DataFrame({"filtre_kodu": ["F1"], "hisse_kodu": ["AAA"]}),
        pd.DataFrame({"filtre_kodu": ["F1"], "hisse_kodu": ["BBB"]}),
    ]
    detay_df = _build_detay_df(detay_list, trades)
    critical = ["hisse_kodu", "getiri_%", "basari", "strateji", "sebep_kodu"]
    # ensure none of the critical columns contain missing values
    assert detay_df[critical].notna().all().all()
