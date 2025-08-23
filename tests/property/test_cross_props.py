import pandas as pd
from hypothesis import given, strategies as st

from backtest.filters.engine import cross_up, cross_down


@given(
    st.lists(
        st.tuples(
            st.floats(allow_nan=False, allow_infinity=False),
            st.floats(allow_nan=False, allow_infinity=False),
        ),
        min_size=3,
    )
)
def test_cross_up_down_do_not_overlap(pairs):
    a_vals = [p[0] for p in pairs]
    b_vals = [p[1] for p in pairs]
    s1 = pd.Series(a_vals)
    s2 = pd.Series(b_vals)
    up = cross_up(s1, s2)
    down = cross_down(s1, s2)
    assert not (up & down).any()
