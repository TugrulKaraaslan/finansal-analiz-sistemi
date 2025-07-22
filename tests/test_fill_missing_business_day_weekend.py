import pandas as pd

from src.preprocessor import fill_missing_business_day


def test_fill_missing_business_day_handles_weekend():
    df = pd.DataFrame({"tarih": [pd.NaT, pd.to_datetime("06.01.2024", dayfirst=True)]})
    out = fill_missing_business_day(df, date_col="tarih")
    assert out.loc[0, "tarih"] == pd.to_datetime("05.01.2024", dayfirst=True)
