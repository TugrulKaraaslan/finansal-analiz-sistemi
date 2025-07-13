"""Tests verifying logger configuration and output.

These assertions ensure that messages propagate to configured handlers and
that log level filtering behaves as expected.
"""

import logging

from finansal_analiz_sistemi.logging_config import get_logger


def test_info_log_emitted(caplog):
    """Configured logger should emit info messages to handlers."""
    logger = get_logger("dummy")
    with caplog.at_level(logging.INFO):
        logger.info("Saved report to XYZ")
    assert "Saved report to XYZ" in caplog.text
