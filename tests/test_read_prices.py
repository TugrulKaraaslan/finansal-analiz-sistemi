import pandas as pd

from finansal_analiz_sistemi import data_loader


def test_read_prices_detects_delimiter(tmp_path):
    csv = tmp_path / "p.csv"
    df = pd.DataFrame({"code": ["AAA"], "date": ["2025-01-01"], "open": [1]})
    df.to_csv(csv, sep=";", index=False)
    out = data_loader.read_prices(csv)
    assert list(out.columns) == ["code", "date", "open"]

    csv2 = tmp_path / "p2.csv"
    df.to_csv(csv2, index=False)
    out2 = data_loader.read_prices(csv2)
    assert list(out2.columns) == ["code", "date", "open"]
