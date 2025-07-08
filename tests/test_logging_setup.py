import io
import logging
import time

from finansal_analiz_sistemi.log_tools import (
    CounterFilter,
    DuplicateFilter,
    setup_logger,
)


def test_utils_setup_logger_adds_duplicate_filter_and_disables_propagation():
    """Test test_utils_setup_logger_adds_duplicate_filter_and_disables_propagation."""
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_filters = root.filters[:]
    old_propagate = root.propagate

    root.handlers.clear()
    root.filters.clear()
    root.propagate = True
    root.setLevel(logging.INFO)

    counter = setup_logger()

    assert isinstance(counter, CounterFilter)
    assert root.propagate is False
    assert any(isinstance(f, DuplicateFilter) for h in root.handlers for f in h.filters)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(DuplicateFilter(window=0.2))
    root.addHandler(handler)

    root.info("dup")
    root.info("dup")
    time.sleep(0.25)
    root.info("dup")

    lines = [line for line in stream.getvalue().splitlines() if "dup" in line]
    assert len(lines) == 2
    logging.shutdown()
    root.handlers.clear()
    root.filters.clear()
    root.propagate = old_propagate
    for h in old_handlers:
        root.addHandler(h)
    for f in old_filters:
        root.addFilter(f)
