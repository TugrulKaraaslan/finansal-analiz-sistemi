import io
import logging
import time

from finansal_analiz_sistemi.log_tools import DuplicateFilter


def test_duplicate_filter():
    logger = logging.getLogger("dup")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    logger.addFilter(DuplicateFilter(window=0.5))
    logger.propagate = False

    logger.info("hey")
    logger.info("hey")
    time.sleep(0.6)
    logger.info("hey")

    lines = [line for line in stream.getvalue().splitlines() if "hey" in line]
    assert len(lines) == 2
