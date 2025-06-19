import warnings
import pandas as pd
import contextlib
import io
import pytest

# pytest sırasında açık dosya uyarısını bastır
warnings.filterwarnings(
    "ignore",
    message="Exception ignored in: <_io.FileIO",
    category=pytest.PytestUnraisableExceptionWarning,
)
