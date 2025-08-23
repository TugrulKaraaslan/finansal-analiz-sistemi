.PHONY: fixtures preflight test golden golden-verify lint check dev bench bench-cli profile mem perf-report
actions = fixtures preflight lint test golden-verify

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

.PHONY: quality
quality:
	python tools/validate_data_quality.py
