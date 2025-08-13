import importlib
import sys

RECOMMENDED_CMD = 'pip install "numpy<2.0.0" "pandas<2.2" pandas-ta==0.3.14b0'


def _parse(version: str) -> tuple:
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def _check(pkg: str, max_version: str) -> bool:
    try:
        module = importlib.import_module(pkg)
    except ImportError:
        return True  # missing pkg will be handled by installation
    return _parse(module.__version__) < _parse(max_version)


if __name__ == "__main__":
    issues = []
    if not _check("numpy", "2.0.0"):
        issues.append("numpy>=2.0.0 detected")
    if not _check("pandas", "2.2.0"):
        issues.append("pandas>=2.2.0 detected")
    if issues:
        for issue in issues:
            print(issue)
        print("Please install compatible versions with:")
        print(RECOMMENDED_CMD)
        sys.exit(1)
