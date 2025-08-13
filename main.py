from __future__ import annotations

from io_filters import load_filters_csv


def main() -> None:
    """Entry point."""
    try:
        load_filters_csv("filters.csv")
    except FileNotFoundError:
        print(
            "filters.csv dosyası bulunamadı. Lütfen dosyanın mevcut olduğundan "
            "emin olun."
        )


if __name__ == "__main__":
    main()
