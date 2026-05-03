from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from trading.config import DataConfig
from trading.data import cache as cache_module


def _synthetic_df(n: int = 20) -> pd.DataFrame:
    idx = pd.DatetimeIndex(
        pd.bdate_range("2020-01-02", periods=n).to_numpy(),
        name="Date",
    )
    rng = np.random.default_rng(42)
    close = 100 + rng.standard_normal(n).cumsum()
    high = close + 1.0
    low = close - 1.0
    open_ = np.clip(close + rng.standard_normal(n) * 0.1, low + 0.01, high - 0.01)
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


@pytest.fixture
def data_cfg(tmp_path: Path) -> DataConfig:
    return DataConfig(
        ticker="SPY",
        start_date=date(2020, 1, 2),
        end_date=date(2020, 1, 31),
        cache_path=tmp_path / "raw" / "spy.parquet",
        auto_adjust=True,
    )


def test_first_call_downloads_and_writes(monkeypatch, data_cfg: DataConfig):
    calls = {"n": 0}

    def fake_fetch(**kwargs):
        calls["n"] += 1
        return _synthetic_df()

    monkeypatch.setattr(cache_module, "fetch_ohlc", fake_fetch)

    df = cache_module.load_or_download(data_cfg)

    assert calls["n"] == 1
    assert data_cfg.cache_path.is_file()
    assert len(df) == 20


def test_second_call_hits_cache(monkeypatch, data_cfg: DataConfig):
    calls = {"n": 0}

    def fake_fetch(**kwargs):
        calls["n"] += 1
        return _synthetic_df()

    monkeypatch.setattr(cache_module, "fetch_ohlc", fake_fetch)

    cache_module.load_or_download(data_cfg)
    cache_module.load_or_download(data_cfg)

    assert calls["n"] == 1, "second call must read from parquet, not re-fetch"


def test_refresh_forces_redownload(monkeypatch, data_cfg: DataConfig):
    calls = {"n": 0}

    def fake_fetch(**kwargs):
        calls["n"] += 1
        return _synthetic_df()

    monkeypatch.setattr(cache_module, "fetch_ohlc", fake_fetch)

    cache_module.load_or_download(data_cfg)
    cache_module.load_or_download(data_cfg, refresh=True)

    assert calls["n"] == 2


def test_cache_round_trip_preserves_values(monkeypatch, data_cfg: DataConfig):
    expected = _synthetic_df()
    monkeypatch.setattr(cache_module, "fetch_ohlc", lambda **_: expected)

    written = cache_module.load_or_download(data_cfg)
    read_back = cache_module.load_or_download(data_cfg)

    pd.testing.assert_frame_equal(written, read_back)
