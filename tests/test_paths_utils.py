from utils.paths import resolve_path
import os


def test_resolve_path_accepts_bytes(tmp_path):
    file_path = tmp_path / "a.txt"
    byte_path = os.fsencode(file_path)
    assert resolve_path(byte_path) == file_path.resolve()


def test_resolve_path_type_error():
    class Foo:
        pass
    try:
        resolve_path(Foo())
    except TypeError:
        pass
    else:
        assert False, "TypeError not raised"
