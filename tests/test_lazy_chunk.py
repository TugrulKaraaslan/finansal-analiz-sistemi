"""Tests for the ``lazy_chunk`` helper function."""

import pytest

from finansal.utils import lazy_chunk


def test_lazy_chunk_yields_groups():
    """Chunking should lazily yield tuples of the given size."""
    data = list(range(5))
    chunks = list(lazy_chunk(data, 2))
    assert chunks == [(0, 1), (2, 3), (4,)]


def test_lazy_chunk_invalid_size():
    """Chunk size of zero should raise a ``ValueError``."""
    with pytest.raises(ValueError):
        list(lazy_chunk([1, 2], 0))
