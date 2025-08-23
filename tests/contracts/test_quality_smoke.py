import subprocess
import sys


def test_quality_tool_exits_zero():
    res = subprocess.run([sys.executable, "tools/validate_data_quality.py"])
    assert res.returncode in (0,), res.returncode
