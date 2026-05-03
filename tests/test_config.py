from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from trading.config import Config, load_config, repo_root


def test_load_real_config():
    cfg = load_config(repo_root() / "configs" / "main.yaml")

    assert isinstance(cfg, Config)
    assert cfg.data.ticker == "SPY"
    assert cfg.data.start_date == date(2014, 1, 1)
    assert cfg.data.end_date == date(2024, 12, 31)
    assert cfg.data.auto_adjust is True
    assert cfg.data.cache_path.is_absolute()
    assert cfg.data.cache_path.name == "spy.parquet"

    assert cfg.labels.threshold == pytest.approx(0.003)
    assert cfg.labels.horizon == 1

    assert cfg.costs.commission_bps == 5
    assert cfg.costs.slippage_bps == 1

    assert cfg.validation.train_years == 5
    assert cfg.validation.val_years == 1
    assert cfg.validation.embargo_days == 5


def test_config_is_frozen():
    cfg = load_config(repo_root() / "configs" / "main.yaml")
    with pytest.raises(ValidationError):
        cfg.data.ticker = "QQQ"


def _write_yaml(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(payload))
    return p


def _valid_payload() -> dict:
    return {
        "data": {
            "ticker": "SPY",
            "start_date": "2014-01-01",
            "end_date": "2024-12-31",
            "cache_path": "data/raw/spy.parquet",
            "auto_adjust": True,
        },
        "labels": {"threshold": 0.003, "horizon": 1},
        "costs": {"commission_bps": 5, "slippage_bps": 1},
        "validation": {"train_years": 5, "val_years": 1, "embargo_days": 5},
    }


def test_missing_required_key_raises(tmp_path: Path):
    payload = _valid_payload()
    del payload["data"]["ticker"]
    with pytest.raises(ValidationError):
        load_config(_write_yaml(tmp_path, payload))


def test_unknown_key_raises(tmp_path: Path):
    payload = _valid_payload()
    payload["data"]["typo_field"] = "oops"
    with pytest.raises(ValidationError):
        load_config(_write_yaml(tmp_path, payload))


def test_bad_type_raises(tmp_path: Path):
    payload = _valid_payload()
    payload["labels"]["threshold"] = "not_a_number"
    with pytest.raises(ValidationError):
        load_config(_write_yaml(tmp_path, payload))


def test_inverted_dates_raise(tmp_path: Path):
    payload = _valid_payload()
    payload["data"]["start_date"] = "2024-12-31"
    payload["data"]["end_date"] = "2014-01-01"
    with pytest.raises(ValidationError):
        load_config(_write_yaml(tmp_path, payload))


def test_negative_threshold_raises(tmp_path: Path):
    payload = _valid_payload()
    payload["labels"]["threshold"] = -0.001
    with pytest.raises(ValidationError):
        load_config(_write_yaml(tmp_path, payload))


def test_absolute_cache_path_preserved(tmp_path: Path):
    payload = _valid_payload()
    payload["data"]["cache_path"] = str(tmp_path / "abs" / "spy.parquet")
    cfg = load_config(_write_yaml(tmp_path, payload))
    assert cfg.data.cache_path == tmp_path / "abs" / "spy.parquet"
