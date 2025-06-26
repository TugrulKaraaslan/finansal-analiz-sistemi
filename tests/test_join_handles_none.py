import pytest


def test_join_handles_none():
    data = {"F1": "msg", None: "err"}
    result = ",".join(str(k) for k in data.keys() if k)
    assert result == "F1"
