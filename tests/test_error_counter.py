import logging

from finansal_analiz_sistemi.logging_utils import (
    ERROR_COUNTER,
    ErrorCountingFilter,
)


def test_counter_increments():
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    logger = logging.getLogger("dummy")
    logger.addFilter(ErrorCountingFilter())
    ERROR_COUNTER["errors"] = 0
    ERROR_COUNTER["warnings"] = 0
    logger.error("boom")
    logger.warning("careful")
    assert ERROR_COUNTER["errors"] == 1
    assert ERROR_COUNTER["warnings"] == 1
