# Changelog

## Unreleased
- TEST-04-A: big_df fixture & depth guard.
- Added `max_filter_depth` setting (default 7) for filter recursion control.
- Auto-generated columns like `volume_tl` during preprocessing.
- Failure tracker entries now capture `reason` and `hint`.
- 2025-06-22  Added Excel / Parquet support to filter loader (LOADER-02)
- 2025-06-22  Added Rich color logs for Colab (LOG-03)
- TEST-04-C: memory & rich-logging tests; CI updates.
- TEST-04-B: helper & loader tests.
- Proje OpenBB ile uyumlu hale getirildi, pandas-ta desteği kaldırıldı.
- OpenBB fonksiyon çağrıları için `openbb_missing.py` eklendi.

## [0.9.3] – 2025-06-22
### Added
• MAX_FILTER_DEPTH now user-configurable (default raised 5→ 7).
• Excel / Parquet filter-loader formats; helper columns auto-generated (`volume_tl`, `psar`).
• Rich color logs on Colab when `LOG_SIMPLE` unset.
• Memory-leak regression tests; nightly slow-test job.

### Fixed
• Percentage metrics display correct scale (12.8 % not 1280 %).
• generate_full_report produces stable output under 2 GB RAM.

### Changed
• generate_full_report API returns detailed error sheet + summary.

## [0.9.2] – 2025-06-22
### Fixed
- Reduced peak RAM by ~35 % and cleared global leak points (#MEM-07)
- Added psutil to dev dependencies and made memory test optional if missing (#CI-psutil)

## [0.9.1] – 2025-06-21
### Fixed
- KPI percentage values now display the correct scale (12.8 % not 1280 %) (#KPI-12)
