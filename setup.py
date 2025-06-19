from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).parent


def parse_requirements(path):
    reqs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            reqs.append(line.split()[0])
    return reqs


setup(
    name="finansal-analiz-sistemi",
    version="0.1.0",
    description="Backtest otomasyon projesi",
    long_description=(BASE_DIR / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=[
        "backtest_core",
        "config",
        "data_loader",
        "data_loader_cache",
        "filter_engine",
        "filtre_dogrulama",
        "indicator_calculator",
        "kontrol_araci",
        "log_to_health",
        "main",
        "preprocessor",
        "report_generator",
        "report_stats",
        "report_utils",
    ],
    install_requires=parse_requirements("requirements.txt"),
)
