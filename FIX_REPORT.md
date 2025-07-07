# Fix Report

## Changes Made
- Added `HATALAR_COLUMNS` constant and new helper function `save_hatalar_excel` in `report_generator.py` to standardize writing of the "Hatalar" Excel sheet.
- Updated `_write_error_sheet` to explicitly reindex columns and write using the correct header order.
- Exported `save_hatalar_excel` via `__all__` for public use.
- Added `tests/test_hatalar_sheet_header.py` verifying header alignment of generated Excel files.
- Fixed `filter_engine` to populate `filtre_kod` when logging errors and updated `_write_error_sheet` to retain this column.
- Added regression test ensuring `filtre_kod` values are never empty.

## Root Cause
The "Hatalar" sheet was written without enforcing column order and engine, causing headers to shift during later reads. This resulted in the now-removed `analyse_missing.py` script reporting zero filters due to mismatched column names.

## Resolution
All error-sheet writes now specify `index=False` and column order. A dedicated helper saves the sheet with OpenPyXL, ensuring consistent headers.

## Future Work
Include similar helpers for other Excel outputs and ensure column names remain consistent across the project.

# Fix: populate filtre_kod column in Hatalar sheet
* Root cause: errors.append omitted filtre_kod → NaNs
* Resolution: pass filt.kod when logging QUERY_ERROR, enforce via HATALAR_COLUMNS
* Tests: added regression test_hatalar_sheet_has_filter_ids
* Outcome: the (now-removed) analyse_missing.py script now reports the correct filter count
