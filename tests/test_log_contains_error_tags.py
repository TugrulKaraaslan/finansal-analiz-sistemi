"""Ensure error log messages include diagnostic tags.

These tests confirm that helper routines attach the ``QUERY_ERROR`` tag so
log analysis tools can easily spot issues.
"""

import logging
import re

from filter_engine import run_single_filter


def test_log_has_query_error(tmp_path, caplog):
    """Error logs should contain the ``QUERY_ERROR`` tag."""
    caplog.set_level(logging.WARNING)
    # use a dummy filter to trigger a parse error
    run_single_filter("TERRIBLE_FILTER", "close > df['X']")
    log_text = "\n".join(rec.getMessage() for rec in caplog.records)
    assert re.search(r"QUERY_ERROR:", log_text), "Log QUERY_ERROR etiketi içermiyor"
