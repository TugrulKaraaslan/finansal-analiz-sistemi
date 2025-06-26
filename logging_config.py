"""Compatibility wrapper that re-exports logging helpers."""

from finansal_analiz_sistemi.log_tools import get_logger
from finansal_analiz_sistemi.log_tools import setup_logger as setup_logging

__all__ = ["get_logger", "setup_logging"]
