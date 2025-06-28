"""Compatibility wrapper that re-exports logging helpers."""

# Re-export the rich-aware logging helpers from the package-level module.
from finansal_analiz_sistemi.logging_config import get_logger, setup_logging

__all__ = ["get_logger", "setup_logging"]
