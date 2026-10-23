"""Tests for configuration dataclasses and loader."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from facepong.config.loader import load_config
from facepong.config.settings import AppConfig


def test_default_config_loading() -> None:
    """Ensure default config initializes with valid standard values."""
    config = load_config(Path("config/default.toml"))
    assert isinstance(config, AppConfig)
    assert config.display.width == 1280
    assert config.display.height == 720
    assert config.game.winning_score == 5
    assert config.vision.camera_index == 0
    assert config.vision.model_complexity == 0
    assert config.controls.player1_input == "face"


def test_missing_config_fallback() -> None:
    """Fallback to AppConfig default values if path does not exist."""
    config = load_config(Path("non_existent_file.toml"))
    assert isinstance(config, AppConfig)
    assert config.game.winning_score == 5


def test_partial_toml_override() -> None:
    """Verify that custom TOML overrides target fields correctly."""
    toml_content = b"""
    [game]
    winning_score = 11
    ball_initial_speed = 500.0

    [display]
    width = 1920
    """
    with NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
        tmp.write(toml_content)
        tmp.flush()
        tmp_path = Path(tmp.name)

    try:
        config = load_config(tmp_path)
        assert config.game.winning_score == 11
        assert config.game.ball_initial_speed == 500.0
        assert config.display.width == 1920
        # Untouched sections maintain defaults
        assert config.display.height == 720
    finally:
        tmp_path.unlink()
