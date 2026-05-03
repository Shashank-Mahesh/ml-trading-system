"""Load and validate the project config from a YAML file."""

from __future__ import annotations

from pathlib import Path

import yaml

from trading.config.schema import Config


def repo_root() -> Path:
    """Locate the repository root by walking up to the nearest pyproject.toml."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError("Could not locate repo root (no pyproject.toml found above this file).")


def load_config(path: str | Path) -> Config:
    """Read a YAML config file and return a validated Config object.

    The data.cache_path field is resolved relative to the repo root if it is not
    already absolute, so the resulting path is stable regardless of the caller's
    current working directory.

    Args:
        path: Path to the YAML config file.

    Returns:
        A frozen, validated Config instance.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        pydantic.ValidationError: If the YAML contents fail schema validation.
    """
    path = Path(path)
    with path.open("r") as f:
        raw = yaml.safe_load(f)

    cfg = Config.model_validate(raw)

    if not cfg.data.cache_path.is_absolute():
        resolved = repo_root() / cfg.data.cache_path
        cfg = cfg.model_copy(update={"data": cfg.data.model_copy(update={"cache_path": resolved})})

    return cfg
