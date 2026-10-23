"""Configuration dataclasses for FacePong."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DisplayConfig:
    """Display and rendering configuration."""

    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    fps_target: int = 60
    title: str = "FacePong — Vision Controlled Pong"


@dataclass(frozen=True)
class GameConfig:
    """Gameplay, rules and physics configuration."""

    winning_score: int = 5
    paddle_width: int = 18
    paddle_height: int = 120
    paddle_speed: float = 700.0
    paddle_margin_x: int = 40
    ball_radius: int = 10
    ball_initial_speed: float = 420.0
    ball_max_speed: float = 880.0
    speed_increment: float = 1.06


@dataclass(frozen=True)
class VisionConfig:
    """Computer vision, camera and facial tracking configuration."""

    camera_index: int = 0
    frame_width: int = 320
    frame_height: int = 240
    fps: int = 20
    split_mode: str = "horizontal"
    model_complexity: int = 0
    refine_landmarks: bool = False
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    smoothing_alpha: float = 0.28
    deadzone: float = 0.025
    neutral_ratio: float = 0.45
    sensitivity: float = 3.2


@dataclass(frozen=True)
class ControlsConfig:
    """Input adapters and key mappings."""

    player1_input: str = "face"
    player2_input: str = "face"
    p1_key_up: str = "w"
    p1_key_down: str = "s"
    p2_key_up: str = "up"
    p2_key_down: str = "down"
    invert_pitch: bool = False


@dataclass(frozen=True)
class DebugConfig:
    """Debug metrics and visual overlays."""

    show_hud: bool = True
    show_fps: bool = True
    show_detection_status: bool = True
    show_camera_preview: bool = False
    log_level: str = "INFO"


@dataclass(frozen=True)
class AppConfig:
    """Top-level unified application configuration."""

    display: DisplayConfig = field(default_factory=DisplayConfig)
    game: GameConfig = field(default_factory=GameConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    config_file_path: Path | None = None
