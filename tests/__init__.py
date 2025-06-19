import warnings, pandas as pd, contextlib, io, pytest

# pytest sırasında açık dosya uyarısını bastır
warnings.filterwarnings(
    "ignore",
    message="Exception ignored in: <_io.FileIO",
    category=pytest.PytestUnraisableExceptionWarning,
)
