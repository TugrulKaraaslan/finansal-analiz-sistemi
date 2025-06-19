from logging_config import get_logger


def test_rich_handler_attached():
    logger = get_logger("test")
    assert logger.handlers  # en az 1 handler var

