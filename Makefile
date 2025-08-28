.PHONY: fixtures preflight test golden golden-verify lint check dev-setup bench bench-cli profile mem perf-report guardrails colab
actions = fixtures preflight lint test golden-verify

export LOG_LEVEL ?= INFO
export LOG_FORMAT ?= json

fixtures:
	python tools/make_excel_fixtures.py
preflight:
	python tools/preflight_run.py

guardrails:
	python -m backtest.cli guardrails

test:
	pytest -q

ci:
	bash tools/ci_checks.sh

golden:
	python tools/update_golden_checksums.py

golden-verify: golden
	git diff --exit-code -- tests/golden/checksums.json || (echo "Golden checksums out-of-date. Run: make golden" && exit 1)

lint:
	python tools/lint_filters.py

check:
	$(MAKE) $(actions)

dev-setup:
	pip install -U pip && pip install -e ".[dev]" && pip-sync requirements-py312.lock.txt

colab:
	pip install -U pip && pip install -r requirements-colab.lock.txt

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
	DATA_DIR=data python -m backtest.cli config-validate --export-json-schema

.PHONY: validate
validate: config-validate


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

.PHONY: metrics
metrics:
	python -m backtest.cli eval-metrics --start 2025-03-07 --end 2025-03-11 --horizon-days 5 --threshold-bps 50 --signal-cols entry_long exit_long






.PHONY: risk-smoke
risk-smoke:
	python -c "from backtest.risk.guards import RiskEngine; import pandas as pd; engine = RiskEngine({'enabled': True, 'exposure': {'per_symbol_max_pct': 0.1}}); orders = pd.DataFrame({'fill_price':[100], 'quantity':[200]}); dec = engine.decide({'equity':1e6}, orders, None, equity=1e6, symbol_exposure=0); print(dec.final_action)"
