"""Google Colab setup for project dependencies with logging."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "loglar" / "colab_install.log"
REQ_FILE = ROOT / "requirements-colab.txt"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], log_file) -> None:
    """Run a shell command and log output."""
    subprocess.run(cmd, check=True, stdout=log_file, stderr=subprocess.STDOUT)


with LOG_PATH.open("w") as log_file:
    run([sys.executable, "-m", "pip", "install", "-U", "pip"], log_file)
    run([sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)], log_file)
