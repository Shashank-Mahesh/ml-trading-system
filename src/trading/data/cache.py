"""Cache-first loader for the OHLCV dataset."""

from __future__ import annotations

import pandas as pd

from trading.config import DataConfig
from trading.data.download import fetch_ohlc
from trading.data.validate import validate_ohlc


def load_or_download(config: DataConfig, refresh: bool = False) -> pd.DataFrame:
    """Return the OHLCV DataFrame, reading from parquet cache when possible.

    Reads `config.cache_path` if it exists and `refresh` is False. Otherwise
    downloads via yfinance, validates the result, writes to parquet, and
    returns the DataFrame.

    Args:
        config: DataConfig section with ticker, dates, cache path, adjust flag.
        refresh: If True, force a fresh download even if the cache exists.

    Returns:
        Validated OHLCV DataFrame.
    """
    cache_path = config.cache_path

    if not refresh and cache_path.is_file():
        df = pd.read_parquet(cache_path)
        validate_ohlc(df)
        return df

    df = fetch_ohlc(
        ticker=config.ticker,
        start=config.start_date,
        end=config.end_date,
        auto_adjust=config.auto_adjust,
    )
    validate_ohlc(df)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)

    return df
