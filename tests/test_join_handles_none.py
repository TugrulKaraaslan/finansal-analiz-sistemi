"""Unit tests for join_handles_none."""


def test_join_handles_none():
    """Test test_join_handles_none."""
    data = {"F1": "msg", None: "err"}
    result = ",".join(str(k) for k in data.keys() if k)
    assert result == "F1"
