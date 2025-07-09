"""Command-line interface for Parquet cache management."""

from __future__ import annotations

import logging
from pathlib import Path

import click

import cache_builder
import data_loader
from finansal.parquet_cache import ParquetCacheManager
from finansal_analiz_sistemi import config
from indicator_calculator import calculate_chunked


@click.command(help="Parquet cache yoneticisi")
@click.option(
    "--csv", "csv_path", type=click.Path(exists=True), default=config.DEFAULT_CSV_PATH
)
@click.option("--cache-path", type=click.Path(), default=config.CACHE_PATH)
@click.option(
    "--refresh-cache",
    is_flag=True,
    default=False,
    help="Cache’i CSV’den yeniden olustur",
)
@click.option(
    "--rebuild-cache",
    is_flag=True,
    default=False,
    help="veri/ham klasorunden Parquet cache'i yeniden olustur",
)
@click.option("--ind-set", type=click.Choice(["core", "full"]), default="core")
@click.option("--chunk-size", type=int, default=config.CHUNK_SIZE)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Log seviyesi",
)
def main(
    csv_path: str,
    cache_path: str,
    refresh_cache: bool,
    rebuild_cache: bool,
    ind_set: str,
    chunk_size: int,
    log_level: str,
) -> None:
    """Run the CLI to manage the Parquet cache and compute indicators."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    manager = ParquetCacheManager(Path(cache_path))

    if rebuild_cache:
        cache_builder.build()
        df = data_loader.load_dataset()
    elif refresh_cache or not Path(cache_path).exists():
        df = manager.refresh(Path(csv_path))
    else:
        df = manager.load()

    click.echo(f"Veri satir sayisi: {len(df):,}")

    full_inds = (
        config.CORE_INDICATORS
        + [f"ema_{n}" for n in (50, 100, 200)]
        + [f"sma_{n}" for n in (50, 100, 200)]
    )
    active = config.CORE_INDICATORS if ind_set == "core" else full_inds
    calculate_chunked(df, active, chunk_size=chunk_size)


if __name__ == "__main__":  # pragma: no cover
    main()
