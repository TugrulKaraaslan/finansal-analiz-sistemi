"""Ensure dependency versions match across requirement files and ``pyproject``.

The script compares ``requirements.txt`` and ``requirements-colab.txt`` with
the ``[tool.poetry.dependencies]`` section of ``pyproject.toml``.  Any
discrepancies between these sources cause a non-zero exit status so that CI
jobs can detect version drift early.
"""

import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
req_main = root / "requirements.txt"
req_colab = root / "requirements-colab.txt"
pyproject = root / "pyproject.toml"

# pattern to parse requirement lines pkg==version or pkg (no version)
_pat = re.compile(r"^([A-Za-z0-9_.-]+)(?:==([^=]+))?$")


def parse_requirements(path: Path) -> dict[str, str]:
    """Return a mapping of package names to pinned versions.

    Parameters
    ----------
    path : Path
        Requirements file to parse.

    Returns
    -------
    dict[str, str]
        Package names mapped to their pinned version strings. Missing
        versions are stored as an empty string.
    """
    pkgs = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _pat.match(line)
        if not m:
            continue
        name, ver = m.groups()
        pkgs[name.lower()] = ver or ""
    return pkgs


main_pkgs = parse_requirements(req_main)
colab_pkgs = parse_requirements(req_colab)

failed = False
if main_pkgs != colab_pkgs:
    missing = set(main_pkgs.items()) ^ set(colab_pkgs.items())
    print("Version mismatch between requirements.txt and requirements-colab.txt:")
    for pkg, ver in missing:
        print(f"  {pkg} -> {ver}")
    failed = True

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

proj_data = tomllib.loads(pyproject.read_text())
poetry_deps = proj_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
for name, ver in poetry_deps.items():
    if name == "python":
        continue
    expected = main_pkgs.get(name.lower())
    ver_str = str(ver)
    if expected is None:
        continue
    if expected and expected not in ver_str:
        print(
            f"Version mismatch for {name}: pyproject.toml has {ver_str}, requirements.txt has {expected}"
        )
        failed = True

if failed:
    sys.exit(1)
print("Dependency versions are consistent.")
