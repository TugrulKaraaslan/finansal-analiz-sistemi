import os
import importlib
import logging
from rich.console import Console
from rich.logging import RichHandler
from finansal_analiz_sistemi import logging_config


def _capture(msg: str) -> str:
    import io

    buf = io.StringIO()
    if os.getenv("LOG_SIMPLE"):
        handler = logging.StreamHandler(buf)
    else:
        console = Console(file=buf, force_terminal=True)
        handler = RichHandler(console=console, show_time=False, rich_tracebacks=True)
    logger = logging_config.setup_logging()
    logger.handlers = [handler]
    logger.warning(msg)
    return buf.getvalue()


def test_rich_enabled(monkeypatch):
    monkeypatch.delenv("LOG_SIMPLE", raising=False)
    monkeypatch.setattr("finansal_analiz_sistemi.config.IS_COLAB", True)
    importlib.reload(logging_config)  # reload to apply monkeypatch
    out = _capture("warn")
    assert "\x1b[" in out


def test_rich_disabled(monkeypatch):
    monkeypatch.setenv("LOG_SIMPLE", "1")
    importlib.reload(logging_config)
    out = _capture("warn")
    assert "\x1b[" not in out


def test_rich_handler_added(monkeypatch):
    monkeypatch.delenv("LOG_SIMPLE", raising=False)
    monkeypatch.setattr("finansal_analiz_sistemi.config.IS_COLAB", True)
    logging.getLogger().handlers.clear()
    importlib.reload(logging_config)
    log = logging_config.get_logger("t")
    assert any(h.__class__.__name__ == "RichHandler" for h in log.handlers)
