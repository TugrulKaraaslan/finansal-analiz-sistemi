from utils.env_utils import positive_int_env


def test_env_whitespace(monkeypatch):
    monkeypatch.setenv("TEST_INT_ENV", " 42 ")
    assert positive_int_env("TEST_INT_ENV", 1) == 42
    monkeypatch.delenv("TEST_INT_ENV", raising=False)


def test_env_invalid(monkeypatch):
    monkeypatch.setenv("TEST_INT_ENV", "notanint")
    assert positive_int_env("TEST_INT_ENV", 5) == 5
    monkeypatch.setenv("TEST_INT_ENV", "-3")
    assert positive_int_env("TEST_INT_ENV", 7) == 7
    monkeypatch.delenv("TEST_INT_ENV", raising=False)
