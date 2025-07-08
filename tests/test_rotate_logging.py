"""Tests for log rotation utilities."""

import logging
from logging.handlers import RotatingFileHandler

from finansal_analiz_sistemi import log_tools as logging_setup


def test_log_rotation(tmp_path, monkeypatch):
    """Test test_log_rotation."""
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_filters = root.filters[:]
    root.handlers.clear()
    root.filters.clear()
    monkeypatch.chdir(tmp_path)

    class TinyHandler(RotatingFileHandler):
        """Rotate log files aggressively for testing."""

        def __init__(self, filename, *args, **kwargs):
            """Test __init__."""
            super().__init__(filename, maxBytes=200, backupCount=1, encoding="utf-8")

    monkeypatch.setattr(logging_setup, "RotatingFileHandler", TinyHandler)

    logging_setup.setup_logger()
    log = logging.getLogger("rotate")
    for i in range(50):
        log.info("%d %s", i, "x" * 20)
    logging.shutdown()

    log_dir = tmp_path / "loglar"
    assert (log_dir / "rapor.log").exists()
    assert (log_dir / "rapor.log.1").exists()

    root.handlers.clear()
    root.filters.clear()
    for h in old_handlers:
        root.addHandler(h)
    for f in old_filters:
        root.addFilter(f)
