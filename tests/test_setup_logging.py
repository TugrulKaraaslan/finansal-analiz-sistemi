"""Test module for test_setup_logging."""

import io
import logging
import time

from finansal_analiz_sistemi import log_tools
from finansal_analiz_sistemi.log_tools import DuplicateFilter, setup_logging


def test_setup_logging_deduplicates_and_sets_propagate():
    """Test test_setup_logging_deduplicates_and_sets_propagate."""
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_filters = root.filters[:]
    old_propagate = root.propagate

    root.handlers.clear()
    root.filters.clear()
    root.propagate = True
    root.setLevel(logging.INFO)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    root.addHandler(handler)

    setup_logging(window=0.2, pct_step=7)

    assert root.propagate is False
    assert any(isinstance(f, DuplicateFilter) for f in root.filters)
    assert log_tools.PCT_STEP == 7

    root.info("dup")
    root.info("dup")
    time.sleep(0.25)
    root.info("dup")

    lines = [line for line in stream.getvalue().splitlines() if "dup" in line]
    assert len(lines) == 2

    root.handlers.clear()
    root.filters.clear()
    root.propagate = old_propagate
    for h in old_handlers:
        root.addHandler(h)
    for f in old_filters:
        root.addFilter(f)
