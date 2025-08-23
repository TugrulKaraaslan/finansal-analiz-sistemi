.PHONY: fixtures preflight test golden golden-verify lint check dev bench bench-cli profile mem perf-report
actions = fixtures preflight lint test golden-verify

export LOG_LEVEL ?= INFO
export LOG_FORMAT ?= json

fixtures:
	python tools/make_excel_fixtures.py
preflight:
	python tools/preflight_run.py

test:
	pytest -q

golden:
	python tools/update_golden_checksums.py

golden-verify: golden
	git diff --exit-code -- tests/golden/checksums.json || (echo "Golden checksums out-of-date. Run: make golden" && exit 1)

lint:
	python tools/lint_filters.py

check:
	$(MAKE) $(actions)

dev:
	pip install -r requirements.txt || true
	pip install -r requirements-dev.txt

bench:
	pytest -q -k perf --benchmark-only

bench-cli:
	python tools/benchmark_scan.py

profile:
	python tools/profile_pyinstrument.py

mem:
	python tools/memory_snapshot.py

perf-report: bench bench-cli profile mem

.PHONY: config-validate
config-validate:
	EXCEL_DIR=veri_guncel_fix python -m backtest.cli config-validate --export-json-schema

.PHONY: logs
logs:
@echo "Log dosyaları: artifacts/logs/"
	@ls -1 artifacts/logs || true

.PHONY: quality
quality:
	python tools/validate_data_quality.py


.PHONY: walk-forward
walk-forward:
	python tools/walk_forward_eval.py

.PHONY: portfolio-sim
portfolio-sim:
	python -m backtest.cli portfolio-sim --config config/colab_config.yaml --portfolio config/portfolio.yaml --start 2025-03-07 --end 2025-03-09

.PHONY: report
report:
	python tools/build_html_report.py

.PHONY: daily
# Istanbul takvimine göre dünü tarar
daily:
	python tools/daily_incremental.py
