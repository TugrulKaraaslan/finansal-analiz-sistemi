import os
import pytest

from utils.paths import resolve_path


def test_resolve_path_accepts_bytes(tmp_path):
    file_path = tmp_path / "a.txt"
    byte_path = os.fsencode(file_path)
    assert resolve_path(byte_path) == file_path.resolve()


def test_resolve_path_type_error():
    class Foo:
        pass

    with pytest.raises(TypeError):
        resolve_path(Foo())
