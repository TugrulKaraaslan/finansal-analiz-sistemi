import hashlib
import json
import os


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def test_golden_files_exist_and_match():
    paths = []
    for p in ['perf_notes.md']:
        if os.path.exists(p):
            paths.append(p)
    if os.path.isdir('loglar'):
        logs = sorted(os.path.join('loglar', x) for x in os.listdir('loglar'))[-2:]
        paths.extend(logs)
    golden_path = 'tests/golden/checksums.json'
    assert os.path.exists(golden_path), 'missing golden checksums.json'
    data = json.load(open(golden_path))
    for p in paths:
        if os.path.exists(p):
            assert p in data, f'{p} not in golden'
            assert sha256(p) == data[p], f'hash mismatch for {p}'
