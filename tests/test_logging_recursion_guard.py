import warnings
from backtest.logging_conf import setup_logger


def test_warning_does_not_recurse(tmp_path):
    setup_logger(log_dir=tmp_path, capture_warnings=True)
    warnings.warn("deprecated thing", DeprecationWarning)
    assert True
