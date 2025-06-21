# Changelog

## Unreleased
- Added `max_filter_depth` setting (default 7) for filter recursion control.
- Auto-generated columns like `volume_tl` during preprocessing.
- Failure tracker entries now capture `reason` and `hint`.

## [0.9.2] – 2025-06-22
### Fixed
- Reduced peak RAM by ~35 % and cleared global leak points (#MEM-07)

## [0.9.1] – 2025-06-21
### Fixed
- KPI percentage values now display the correct scale (12.8 % not 1280 %) (#KPI-12)
