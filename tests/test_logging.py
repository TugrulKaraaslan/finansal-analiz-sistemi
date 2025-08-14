from backtest.logging_utils import setup_logger, Timer
import logging, os


def test_setup_logger_creates_file(tmp_path):
    log_dir = tmp_path / "logs"
    path = setup_logger(run_id="test", log_dir=str(log_dir))
    assert os.path.exists(path)
    with Timer("unit-step"):
        logging.info("hello")
