"""Configuration loader supporting TOML files with typed defaults."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

from facepong.config.settings import (
    AppConfig,
    ControlsConfig,
    DebugConfig,
    DisplayConfig,
    GameConfig,
    VisionConfig,
)

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("config/default.toml")


def _filter_dict(data: dict[str, Any], dataclass_cls: type) -> dict[str, Any]:
    """Filter dictionary keys to match dataclass fields."""
    import inspect

    field_names = inspect.signature(dataclass_cls).parameters.keys()
    return {k: v for k, v in data.items() if k in field_names}


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load configuration from a TOML file or return defaults.

    Args:
        path: Optional file path to TOML configuration.
            If None, attempts to load from DEFAULT_CONFIG_PATH.

    Returns:
        Fully populated and typed AppConfig instance.
    """
    target_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH

    if not target_path.exists():
        logger.warning(
            "Configuration file not found at %s. Using default configuration.", target_path
        )
        return AppConfig()

    try:
        with open(target_path, "rb") as f:
            raw = tomllib.load(f)
    except Exception as exc:
        logger.error(
            "Failed to parse TOML configuration at %s: %s. Using defaults.", target_path, exc
        )
        return AppConfig()

    display_data = _filter_dict(raw.get("display", {}), DisplayConfig)
    game_data = _filter_dict(raw.get("game", {}), GameConfig)
    vision_data = _filter_dict(raw.get("vision", {}), VisionConfig)
    controls_data = _filter_dict(raw.get("controls", {}), ControlsConfig)
    debug_data = _filter_dict(raw.get("debug", {}), DebugConfig)

    return AppConfig(
        display=DisplayConfig(**display_data),
        game=GameConfig(**game_data),
        vision=VisionConfig(**vision_data),
        controls=ControlsConfig(**controls_data),
        debug=DebugConfig(**debug_data),
        config_file_path=target_path.resolve(),
    )
