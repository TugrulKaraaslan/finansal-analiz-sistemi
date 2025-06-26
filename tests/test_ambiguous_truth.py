import pandas as pd


    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA", "BBB"],
            "tarih": [pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01")],
            "close": [1, 2],
        }
    )
        {
            "hisse_kodu": ["AAA", "BBB"],
            "tarih": [pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01")],
            "close": [1, 2],
        }
    )
    filters = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 0"]})
    out, _ = filter_engine.uygula_filtreler(df, filters, pd.Timestamp("2025-01-01"))
    assert out["F1"]["sebep"] == "OK"
