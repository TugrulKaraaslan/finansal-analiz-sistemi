# Alias Policy

Legacy indicator names are normalized to canonical forms before filter evaluation. Using a legacy alias emits a warning and the canonical name is used in computations.

## Supported Legacy Names

| Legacy | Canonical |
| --- | --- |
| its_9 | ichimoku_conversionline |
| iks_26 | ichimoku_baseline |
| macd_12_26_9 | macd_line |
| macds_12_26_9 | macd_signal |
| bbm_20 2 | bbm_20_2 |
| bbu_20 2 | bbu_20_2 |
| bbl_20 2 | bbl_20_2 |
| CCI_20_0 | CCI_20 |
| PSARL_0 | PSARL_0_02_0_2 |
| AROONU_<n> | AROON_UP_<n> |
| AROOND_<n> | AROON_DOWN_<n> |

See [canonical_names.md](canonical_names.md) for the full list of canonical columns.
