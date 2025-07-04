import importlib.util


def test_pandas_ta_installed():
    assert importlib.util.find_spec("pandas_ta") is not None
