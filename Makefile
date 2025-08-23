.PHONY: fixtures preflight test golden golden-verify lint check dev
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
