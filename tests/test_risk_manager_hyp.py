import pytest

try:  # pytest < 8 does not support allow_module_level
    pytest.importorskip("hypothesis", allow_module_level=True)
except TypeError:  # pragma: no cover - fallback
    pytest.importorskip("hypothesis")

import pandas as pd  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

import src.kontrol_araci as kontrol_araci  # noqa: E402
from src.preprocessor import fill_missing_business_day  # noqa: E402

min_dt = pd.Timestamp("1970-01-01").to_pydatetime()
max_dt = pd.Timestamp("2262-04-11").to_pydatetime()


@given(
    st.lists(
        st.one_of(
            st.none(),
            st.datetimes(min_value=min_dt, max_value=max_dt, timezones=st.none()),
        ),
        min_size=1,
    )
)
def test_fill_missing_business_day_no_nulls(dates):
    df = pd.DataFrame({"tarih": dates})
    result = fill_missing_business_day(df)
    if pd.Series(dates).notna().any():
        assert result["tarih"].notna().all()
    else:
        assert result["tarih"].isna().all()


@given(
    st.integers(min_value=0, max_value=100),
    st.lists(st.floats(0, 100), min_size=1, max_size=20),
)
def test_tarama_denetimi_counts_selected(threshold, closes):
    df_filtreler = pd.DataFrame({"kod": ["F"], "PythonQuery": [f"close > {threshold}"]})
    df_ind = pd.DataFrame({"close": closes})
    result = kontrol_araci.tarama_denetimi(df_filtreler, df_ind)
    selected = sum(c > threshold for c in closes)
    assert int(result.loc[0, "secim_adedi"]) == selected
