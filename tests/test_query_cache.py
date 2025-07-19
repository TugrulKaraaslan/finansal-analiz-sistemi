"""Tests for _extract_query_columns caching."""

import filter_engine


def test_query_columns_cache():
    query = "close > 0"
    filter_engine._extract_query_columns.cache_clear()
    filter_engine._extract_query_columns(query)
    before = filter_engine._extract_query_columns.cache_info().hits
    filter_engine._extract_query_columns(query)
    after = filter_engine._extract_query_columns.cache_info().hits
    assert after - before == 1
