import numpy as np
import pandas as pd
import pytest

from trading.data import validate_ohlc


def _good_df(n: int = 10) -> pd.DataFrame:
    idx = pd.DatetimeIndex(
        pd.bdate_range("2020-01-02", periods=n).to_numpy(),
        name="Date",
    )
    rng = np.random.default_rng(0)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + 1.0
    low = close - 1.0
    open_ = close + rng.standard_normal(n) * 0.1
    open_ = np.clip(open_, low + 0.01, high - 0.01)
    return pd.DataFrame(
        {
            "Open": open_,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": rng.integers(1_000_000, 5_000_000, size=n),
        },
        index=idx,
    )


def test_happy_path():
    validate_ohlc(_good_df())


def test_missing_column_raises():
    df = _good_df().drop(columns=["Close"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_ohlc(df)


def test_null_close_raises():
    df = _good_df()
    df.iloc[3, df.columns.get_loc("Close")] = np.nan
    with pytest.raises(ValueError, match="Null values"):
        validate_ohlc(df)


def test_duplicate_dates_raise():
    df = _good_df()
    df.index = pd.DatetimeIndex([df.index[0]] * len(df), name="Date")
    with pytest.raises(ValueError, match="Duplicate dates"):
        validate_ohlc(df)


def test_high_below_low_raises():
    df = _good_df()
    df.iloc[2, df.columns.get_loc("High")] = df.iloc[2, df.columns.get_loc("Low")] - 1
    with pytest.raises(ValueError, match="High < Low"):
        validate_ohlc(df)


def test_high_below_close_raises():
    df = _good_df()
    df.iloc[2, df.columns.get_loc("High")] = df.iloc[2, df.columns.get_loc("Close")] - 0.5
    with pytest.raises(ValueError, match="High is below"):
        validate_ohlc(df)


def test_negative_volume_raises():
    df = _good_df()
    df.iloc[2, df.columns.get_loc("Volume")] = -1
    with pytest.raises(ValueError, match="Negative volume"):
        validate_ohlc(df)


def test_non_monotonic_index_raises():
    df = _good_df()
    df = df.iloc[[0, 2, 1, 3, 4, 5, 6, 7, 8, 9]]
    with pytest.raises(ValueError, match="monotonically increasing"):
        validate_ohlc(df)


def test_non_datetime_index_raises():
    df = _good_df().reset_index(drop=True)
    with pytest.raises(ValueError, match="DatetimeIndex"):
        validate_ohlc(df)


def test_weekend_date_raises():
    df = _good_df(n=5)
    new_idx = df.index.tolist()
    new_idx[2] = pd.Timestamp("2020-01-04")  # Saturday
    df.index = pd.DatetimeIndex(new_idx, name="Date")
    df = df.sort_index()
    with pytest.raises(ValueError, match="Non-weekday"):
        validate_ohlc(df)


def test_validator_does_not_modify_input():
    df = _good_df()
    snapshot = df.copy()
    validate_ohlc(df)
    pd.testing.assert_frame_equal(df, snapshot)
