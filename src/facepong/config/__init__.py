"""Configuration module for FacePong."""

from facepong.config.loader import load_config
from facepong.config.settings import (
    AppConfig,
    ControlsConfig,
    DebugConfig,
    DisplayConfig,
    GameConfig,
    VisionConfig,
)

__all__ = [
    "AppConfig",
    "ControlsConfig",
    "DebugConfig",
    "DisplayConfig",
    "GameConfig",
    "VisionConfig",
    "load_config",
]
