"""Check that summary counts appear in log output."""

import logging
import os
import sys

from finansal_analiz_sistemi.log_tools import setup_logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_log_summary_present(caplog):
    """Test test_log_summary_present."""
    log_counter = setup_logger()
    logger = logging.getLogger("summary_test")
    logger.setLevel(logging.INFO)
    with caplog.at_level(logging.INFO):
        logger.warning("warn")
        summary = (
            f"LOG_SUMMARY | errors={log_counter.errors} | "
            f"warnings={log_counter.warnings} | atlanan_filtre="
        )
        logger.info(summary)

    lines = [line for line in caplog.text.splitlines() if "LOG_SUMMARY" in line]
    assert any("errors=" in line and "atlanan_filtre=" in line for line in lines)
    assert log_counter.errors == 0
    assert log_counter.warnings <= 5
