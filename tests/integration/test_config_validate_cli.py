import subprocess
import sys


def test_config_validate_cli():
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "backtest.cli",
            "config-validate",
            "--config",
            "config/colab_config.yaml",
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode in (0, 2)
