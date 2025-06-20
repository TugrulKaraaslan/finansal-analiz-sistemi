import logging
from logging_config import get_logger


def test_info_log_emitted(caplog):
    logger = get_logger("dummy")
    with caplog.at_level(logging.INFO):
        logger.info("Saved report to XYZ")
    assert "Saved report to XYZ" in caplog.text
