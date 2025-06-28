"""Convenience exports for :mod:`finansal` package."""

from importlib import import_module

ParquetCacheManager = import_module("finansal.parquet_cache").ParquetCacheManager
lazy_chunk = import_module("finansal.utils").lazy_chunk
safe_set = import_module("finansal.utils").safe_set

__all__ = ["ParquetCacheManager", "lazy_chunk", "safe_set"]
