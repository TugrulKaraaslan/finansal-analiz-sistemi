import importlib


def test_pandas_ta_available():
    assert importlib.util.find_spec("pandas_ta") is not None
