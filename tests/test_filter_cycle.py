"""Unit tests for filter_cycle."""

import pytest

import filter_engine as fe


def test_cycle_detection():
    """Test test_cycle_detection."""
    fe.FILTER_DEFS.clear()
    fe.FILTER_DEFS["filter_with_self_loop"] = {"children": ["filter_with_self_loop"]}
    with pytest.raises(fe.CyclicFilterError):
        fe.evaluate_filter("filter_with_self_loop")


def test_depth_limit():
    """Test test_depth_limit."""
    fe.FILTER_DEFS.clear()
    # build chain F0 -> F1 -> ... -> F16 (16 levels)
    for i in range(16):
        fe.FILTER_DEFS[f"F{i}"] = {"children": [f"F{i+1}"] if i < 15 else []}
    with pytest.raises(fe.MaxDepthError):
        fe.evaluate_filter("F0")
