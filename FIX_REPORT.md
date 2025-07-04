# Fix Report

## Changes Made
- Added `HATALAR_COLUMNS` constant and new helper function `save_hatalar_excel` in `report_generator.py` to standardize writing of the "Hatalar" Excel sheet.
- Updated `_write_error_sheet` to explicitly reindex columns and write using the correct header order.
- Exported `save_hatalar_excel` via `__all__` for public use.
- Added `tests/test_hatalar_sheet_header.py` verifying header alignment of generated Excel files.

## Root Cause
The "Hatalar" sheet was written without enforcing column order and engine, causing headers to shift during later reads. This resulted in `analyse_missing.py` reporting zero filters due to mismatched column names.

## Resolution
All error-sheet writes now specify `index=False` and column order. A dedicated helper saves the sheet with OpenPyXL, ensuring consistent headers.

## Future Work
Include similar helpers for other Excel outputs and ensure column names remain consistent across the project.
