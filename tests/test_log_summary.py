import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from utils.logging_setup import setup_logger


def test_log_summary_present(caplog):
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
    assert "LOG_SUMMARY" in caplog.text
    assert log_counter.errors == 0
    assert log_counter.warnings <= 5
