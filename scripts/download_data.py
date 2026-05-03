"""CLI entry point: download (or load from cache) the OHLCV dataset to parquet."""

from __future__ import annotations

import argparse
from pathlib import Path

from trading.config import load_config
from trading.data import load_or_download


def main() -> None:
    """Parse CLI args, load config, fetch (or read from cache), and print a summary."""
    parser = argparse.ArgumentParser(description="Download and cache OHLCV data.")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the YAML config file (e.g. configs/main.yaml).",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-download even if a cached parquet already exists.",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    df = load_or_download(cfg.data, refresh=args.refresh)

    print(
        f"{cfg.data.ticker} {df.index.min().date()} -> {df.index.max().date()}, "
        f"{len(df)} rows, cached at {cfg.data.cache_path}"
    )


if __name__ == "__main__":
    main()
