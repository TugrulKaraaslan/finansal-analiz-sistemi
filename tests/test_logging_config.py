import logging

from finansal_analiz_sistemi import logging_config


def test_get_logger_returns_logger():
    """Check that :func:`get_logger` returns a ``logging.Logger`` instance."""
    assert isinstance(logging_config.get_logger("demo"), logging.Logger)
