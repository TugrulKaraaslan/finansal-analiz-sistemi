import logging
import re

from filter_engine import run_single_filter


def test_log_has_query_error(tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    # sahte filtre, parse hatası tetikle
    run_single_filter("TERRIBLE_FILTER", "close > df['X']")
    log_text = "\n".join(rec.getMessage() for rec in caplog.records)
    assert re.search(r"QUERY_ERROR:", log_text), "Log QUERY_ERROR etiketi içermiyor"
