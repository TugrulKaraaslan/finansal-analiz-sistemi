import pytest

from backtest.cli import build_parser


def test_dry_run_requires_filters():
    p = build_parser()
    with pytest.raises(SystemExit):
        p.parse_args(["dry-run"])  # --filters yok → hata


def test_common_flags_present():
    p = build_parser()
    args = p.parse_args(
        [
            "scan-day",
            "--data",
            "data.csv",
            "--date",
            "2024-01-02",
            "--filters",
            "filters.csv",
            "--out",
            "out",
            "--filters-off",
            "--no-write",
        ]
    )
    assert args.filters_off is True
    assert args.no_write is True
