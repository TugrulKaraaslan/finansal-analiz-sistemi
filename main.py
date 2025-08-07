from __future__ import annotations

def main() -> None:
    """Entry point."""
    from lib.validator import validate_filters

    try:
        validate_filters("filters.csv")
    except FileNotFoundError:
        print("filters.csv dosyası bulunamadı. Lütfen dosyanın mevcut olduğundan emin olun.")


if __name__ == "__main__":
    main()
