.PHONY: fixtures preflight test golden lint
fixtures:
	python tools/make_excel_fixtures.py
preflight:
	python -c "from backtest.paths import EXCEL_DIR; from backtest.filters.preflight import validate_filters; from pathlib import Path; validate_filters(Path('filters.csv') if Path('filters.csv').exists() else Path('config/filters.csv'), EXCEL_DIR); print('preflight passed')"

test:
	pytest -q

golden:
	python tools/update_golden_checksums.py

lint:
	python tools/lint_filters.py
