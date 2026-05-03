"""Validation checks for OHLCV DataFrames."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def validate_ohlc(df: pd.DataFrame) -> None:
    """Validate an OHLCV DataFrame, raising on the first failure.

    Checks: required columns present, no nulls, DatetimeIndex monotonically
    increasing with no duplicates, OHLC sanity (high >= open/low/close,
    low <= open/close), non-negative volume, weekday-only dates.

    The function never modifies the input DataFrame; a "fix-it" validator is
    how silent leakage starts.

    Args:
        df: DataFrame to validate.

    Raises:
        ValueError: On the first validation failure, with a specific message.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    nulls = df[list(REQUIRED_COLUMNS)].isna().sum()
    bad = nulls[nulls > 0]
    if len(bad):
        raise ValueError(f"Null values present in columns: {bad.to_dict()}")

    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(f"Index must be a DatetimeIndex, got {type(df.index).__name__}")

    if df.index.has_duplicates:
        dupes = df.index[df.index.duplicated()].tolist()
        raise ValueError(f"Duplicate dates in index: {dupes[:5]}")

    if not df.index.is_monotonic_increasing:
        raise ValueError("Index is not monotonically increasing")

    if (df["High"] < df["Low"]).any():
        bad_idx = df.index[df["High"] < df["Low"]].tolist()
        raise ValueError(f"High < Low on dates: {bad_idx[:5]}")

    if (df["High"] < df["Open"]).any() or (df["High"] < df["Close"]).any():
        raise ValueError("High is below Open or Close on at least one row")

    if (df["Low"] > df["Open"]).any() or (df["Low"] > df["Close"]).any():
        raise ValueError("Low is above Open or Close on at least one row")

    if (df["Volume"] < 0).any():
        raise ValueError("Negative volume on at least one row")

    weekdays = df.index.dayofweek
    if (weekdays >= 5).any():
        bad_idx = df.index[weekdays >= 5].tolist()
        raise ValueError(f"Non-weekday dates in index: {bad_idx[:5]}")
