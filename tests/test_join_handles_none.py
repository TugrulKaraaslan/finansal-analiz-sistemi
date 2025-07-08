"""Unit tests for join_handles_none."""


def test_join_handles_none():
    """Joining dict keys should skip ``None`` values gracefully."""
    data = {"F1": "msg", None: "err"}
    result = ",".join(str(k) for k in data.keys() if k)
    assert result == "F1"
