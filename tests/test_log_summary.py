import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
import logging_setup


def test_log_summary_present(tmp_path, capsys):
    log_counter = logging_setup.setup_logger()
    logger = logging.getLogger("summary_test")
    logger.warning("warn")
    summary = f"LOG_SUMMARY | errors={log_counter.errors} | warnings={log_counter.warnings} | atlanan_filtre="
    logger.info(summary)
    out = capsys.readouterr().out
    assert "LOG_SUMMARY" in out
    assert log_counter.errors == 0
    assert log_counter.warnings <= 5
