"""Download SPY OHLCV bars from yfinance."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import yfinance as yf


def fetch_ohlc(
    ticker: str,
    start: date,
    end: date,
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Download daily OHLCV bars for a single ticker via yfinance.

    Recent yfinance versions return a DataFrame with MultiIndex columns
    `(Price, Ticker)` even for a single ticker; this wrapper flattens to plain
    string columns and normalizes the index to a tz-naive DatetimeIndex of
    midnight dates so downstream code is not surprised by timezones.

    Args:
        ticker: Symbol to fetch (e.g. "SPY").
        start: Inclusive start date.
        end: Inclusive end date. yfinance treats `end` as exclusive, so we add
            one day before passing it through.
        auto_adjust: If True, OHLC values include dividend and split adjustments
            (total-return). Required for fair next-period return labelling on
            dividend-paying assets.

    Returns:
        DataFrame indexed by date with columns Open, High, Low, Close, Volume.
    """
    df = yf.download(
        tickers=ticker,
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),
        auto_adjust=auto_adjust,
        progress=False,
        group_by="column",
        threads=False,
    )

    if df.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker} {start}..{end}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    df.index = pd.DatetimeIndex(df.index).tz_localize(None).normalize()
    df.index.name = "Date"

    return df
