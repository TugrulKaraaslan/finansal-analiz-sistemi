import logging

from finansal_analiz_sistemi import logging_config


def test_get_logger_returns_logger():
    """Test test_get_logger_returns_logger."""
    assert isinstance(logging_config.get_logger("demo"), logging.Logger)
