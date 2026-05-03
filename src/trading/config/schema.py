"""Pydantic schema for the project config loaded from YAML."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class DataConfig(BaseModel):
    """Data source and caching parameters."""

    model_config = _FROZEN

    ticker: str
    start_date: date
    end_date: date
    cache_path: Path
    auto_adjust: bool = True

    @model_validator(mode="after")
    def _check_date_order(self) -> DataConfig:
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class LabelsConfig(BaseModel):
    """Binary-target labelling parameters."""

    model_config = _FROZEN

    threshold: float = Field(gt=0, description="Next-period return threshold for the +class.")
    horizon: int = Field(ge=1, description="Number of bars ahead to predict.")


class CostsConfig(BaseModel):
    """Transaction-cost assumptions in basis points."""

    model_config = _FROZEN

    commission_bps: float = Field(ge=0)
    slippage_bps: float = Field(ge=0)


class ValidationConfig(BaseModel):
    """Walk-forward CV parameters."""

    model_config = _FROZEN

    train_years: int = Field(ge=1)
    val_years: int = Field(ge=1)
    embargo_days: int = Field(ge=0)


class Config(BaseModel):
    """Top-level project config."""

    model_config = _FROZEN

    data: DataConfig
    labels: LabelsConfig
    costs: CostsConfig
    validation: ValidationConfig
