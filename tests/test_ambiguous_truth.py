"""Ensure DataFrame truth evaluation remains unambiguous.

The :func:`filter_engine._extract_query_columns` helper must not rely on the
truth value of a ``DataFrame`` to avoid ``ValueError`` in newer pandas
versions.
"""

import pandas as pd

import filter_engine


def test_no_ambiguous_truth() -> None:
    """Applying a simple filter should not raise 'ambiguous truth value' errors."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA", "BBB"],
            "tarih": [pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01")],
            "close": [1, 2],
        }
    )
    filters = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 0"]})

    out, _ = filter_engine.uygula_filtreler(df, filters, pd.Timestamp("2025-01-01"))

    assert out["F1"]["sebep"] == "OK"
