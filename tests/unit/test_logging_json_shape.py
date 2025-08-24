from backtest.logging_conf import ensure_run_id, get_logger, log_with


def test_json_log_shape(tmp_path, monkeypatch):
    logger = get_logger("test")
    rid = ensure_run_id()
    log_with(logger, "INFO", "hello", foo=1, bar="x")
    assert rid
