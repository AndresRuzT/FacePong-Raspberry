"""Game state machine and gameplay loop coordinator."""

from __future__ import annotations

from enum import Enum, auto

from facepong.config.settings import AppConfig
from facepong.core.ball import Ball
from facepong.core.paddle import Paddle
from facepong.core.score import ScoreManager


class GameState(Enum):
    """Finite states of the game engine."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class Game:
    """Core game coordinator managing paddles, ball physics, score, and state."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize game world according to application configuration.

        Args:
            config: Full application configuration.
        """
        self.config = config
        self.state = GameState.MENU

        screen_w = float(config.display.width)
        screen_h = float(config.display.height)
        pad_w = float(config.game.paddle_width)
        pad_h = float(config.game.paddle_height)
        pad_margin = float(config.game.paddle_margin_x)
        pad_speed = float(config.game.paddle_speed)

        # Player 1 (Left paddle)
        self.paddle1 = Paddle(
            x=pad_margin,
            initial_y=(screen_h - pad_h) / 2.0,
            width=pad_w,
            height=pad_h,
            bounds_height=screen_h,
            speed=pad_speed,
        )

        # Player 2 (Right paddle)
        self.paddle2 = Paddle(
            x=screen_w - pad_margin - pad_w,
            initial_y=(screen_h - pad_h) / 2.0,
            width=pad_w,
            height=pad_h,
            bounds_height=screen_h,
            speed=pad_speed,
        )

        # Central Ball
        self.ball = Ball(
            bounds_width=screen_w,
            bounds_height=screen_h,
            radius=float(config.game.ball_radius),
            initial_speed=float(config.game.ball_initial_speed),
            max_speed=float(config.game.ball_max_speed),
            speed_increment=float(config.game.speed_increment),
        )

        # Score Tracker
        self.score = ScoreManager(winning_score=config.game.winning_score)

    def start_match(self) -> None:
        """Start a new game session or resume from menu."""
        self.state = GameState.PLAYING
        self.score.reset()
        self.paddle1.reset()
        self.paddle2.reset()
        self.ball.reset(direction=1)

    def toggle_pause(self) -> None:
        """Toggle pause state during an active match."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def reset_match(self) -> None:
        """Reset current match and return to playing state."""
        self.score.reset()
        self.paddle1.reset()
        self.paddle2.reset()
        self.ball.reset(direction=1)
        self.state = GameState.PLAYING

    def update(self, dt: float) -> None:
        """Advance game physics and state by delta time.

        Args:
            dt: Delta time in seconds.
        """
        if self.state != GameState.PLAYING:
            return

        # Update paddle kinematics
        self.paddle1.update(dt)
        self.paddle2.update(dt)

        # Advance ball and check for scoring events
        scoring_player = self.ball.update(dt)

        if scoring_player is not None:
            game_over = self.score.add_point(scoring_player)
            if game_over:
                self.state = GameState.GAME_OVER
            else:
                # Launch ball towards the player who just scored
                launch_dir = 1 if scoring_player == 1 else -1
                self.ball.reset(direction=launch_dir)
            return

        # Paddle collision checks
        self.ball.check_paddle_collision(self.paddle1)
        self.ball.check_paddle_collision(self.paddle2)
