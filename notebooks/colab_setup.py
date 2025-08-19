"""Google Colab setup for fixed package versions."""

import subprocess
import sys


def run(cmd: list[str]) -> None:
    """Run a shell command."""
    subprocess.run(cmd, check=True)


# Upgrade pip
run([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip"])

# Install required packages with fixed versions
packages = [
    "pandas==2.2.2",
    "numpy==1.26.4",
    "pandas-ta==0.3.14b",
    "pandera==0.19.3",
    "loguru",
    "xlsxwriter",
    "typing-inspect",
]
run([sys.executable, "-m", "pip", "install", "-q", *packages])

# Verify installations
import pandas as pd  # noqa: E402
import numpy as np  # noqa: E402
import pandas_ta  # noqa: E402

print(pd.__version__)
print(np.__version__)
print(pandas_ta.__version__)
print("Runtime'ı yeniden başlatmanız gerekiyor")
