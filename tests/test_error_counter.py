"""Ensure logging utilities count errors correctly.

These tests use a dummy logger with :class:`ErrorCountingFilter` attached
to verify that both error and warning counters increase as expected.
"""

import logging

from finansal_analiz_sistemi.logging_utils import ERROR_COUNTER, ErrorCountingFilter


def test_counter_increments():
    """Error and warning counts should increment appropriately."""
    ERROR_COUNTER["errors"] = 0
    ERROR_COUNTER["warnings"] = 0
    logger = logging.getLogger("dummy_test")
    logger.propagate = False
    logger.addFilter(ErrorCountingFilter())
    logger.error("boom")
    logger.warning("careful")
    assert ERROR_COUNTER["errors"] == 1
    assert ERROR_COUNTER["warnings"] == 1
