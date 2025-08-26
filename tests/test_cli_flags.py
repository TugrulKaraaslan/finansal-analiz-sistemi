from backtest.cli import build_parser


def test_common_flags_present():
    p = build_parser()
    args = p.parse_args(
        [
            "scan-day",
            "--data",
            "data.csv",
            "--date",
            "2024-01-02",
            "--" "filters-module",
            "io_filters",
            "--" "filters-include",
            "F1",
            "--out",
            "out",
            "--no-write",
        ]
    )
    assert args.filters_module == "io_filters"
    assert args.filters_include == ["F1"]
    assert args.no_write is True
