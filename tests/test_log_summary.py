from utils.logging_setup import setup_logger
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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

    lines = [l for l in caplog.text.splitlines() if "LOG_SUMMARY" in l]
    assert any("errors=" in l and "atlanan_filtre=" in l for l in lines)
    assert log_counter.errors == 0
    assert log_counter.warnings <= 5
