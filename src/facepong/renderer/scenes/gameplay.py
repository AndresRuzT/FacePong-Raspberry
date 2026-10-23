"""Gameplay rendering scene including paddles, ball, and overlay states."""

from __future__ import annotations

import pygame

from facepong.config.settings import DebugConfig
from facepong.core.game import Game, GameState
from facepong.renderer.hud import HUD

# Aesthetic Colors
COLOR_PADDLE_P1 = (90, 200, 250)  # Clean Cyan
COLOR_PADDLE_P2 = (255, 149, 0)  # Vibrant Amber / Orange
COLOR_BALL = (255, 255, 255)  # Pure White
COLOR_OVERLAY = (0, 0, 0, 180)  # Semi-transparent dark overlay
COLOR_VICTORY = (255, 214, 10)  # Gold
COLOR_TEXT = (255, 255, 255)


class GameplayRenderer:
    """Renders active match elements: paddles, ball, and status overlays."""

    def __init__(self, width: int, height: int, debug_config: DebugConfig) -> None:
        """Initialize gameplay renderer.

        Args:
            width: Viewport width.
            height: Viewport height.
            debug_config: Debug configuration settings.
        """
        self.width = width
        self.height = height
        self.hud = HUD(width, height, debug_config)

        self.font_overlay = pygame.font.SysFont("dejavusans,freesansbold,arial", 56, bold=True)
        self.font_sub = pygame.font.SysFont("dejavusans,arial", 24)

    def draw(
        self,
        surface: pygame.Surface,
        game: Game,
        p1_detected: bool,
        p2_detected: bool,
        p1_type: str,
        p2_type: str,
        game_fps: float,
        cv_fps: float,
    ) -> None:
        """Render complete frame for active gameplay.

        Args:
            surface: Display surface.
            game: Core game instance containing paddles and ball.
            p1_detected: Player 1 detection tracking state.
            p2_detected: Player 2 detection tracking state.
            p1_type: Type name of Player 1 adapter ("face" or "keyboard").
            p2_type: Type name of Player 2 adapter.
            game_fps: Current game loop framerate.
            cv_fps: Current vision processing framerate.
        """
        # 1. Court net and background field
        self.hud.draw_net(surface)

        # 2. Scoreboard
        self.hud.draw_scores(surface, game.score.p1_score, game.score.p2_score)

        # 3. Tracking and diagnostics
        self.hud.draw_player_status(surface, p1_detected, p2_detected, p1_type, p2_type)
        self.hud.draw_telemetry(surface, game_fps, cv_fps)

        # 4. Paddle 1 (Left)
        p1_rect = pygame.Rect(
            int(game.paddle1.x),
            int(game.paddle1.y),
            int(game.paddle1.width),
            int(game.paddle1.height),
        )
        pygame.draw.rect(surface, COLOR_PADDLE_P1, p1_rect, border_radius=6)

        # 5. Paddle 2 (Right)
        p2_rect = pygame.Rect(
            int(game.paddle2.x),
            int(game.paddle2.y),
            int(game.paddle2.width),
            int(game.paddle2.height),
        )
        pygame.draw.rect(surface, COLOR_PADDLE_P2, p2_rect, border_radius=6)

        # 6. Central Ball
        pygame.draw.circle(
            surface,
            COLOR_BALL,
            (int(game.ball.x), int(game.ball.y)),
            int(game.ball.radius),
        )

        # 7. Pause Overlay
        if game.state == GameState.PAUSED:
            self._draw_pause_overlay(surface)

        # 8. Game Over Overlay
        elif game.state == GameState.GAME_OVER:
            self._draw_game_over_overlay(surface, game.score.winner)

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        """Render pause dialog overlay."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 175))
        surface.blit(overlay, (0, 0))

        text_surf = self.font_overlay.render("PAUSED", True, COLOR_TEXT)
        surface.blit(
            text_surf,
            (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50),
        )

        sub_surf = self.font_sub.render("PRESS [SPACE] TO RESUME", True, COLOR_PADDLE_P1)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, self.height // 2 + 25),
        )

    def _draw_game_over_overlay(self, surface: pygame.Surface, winner: int | None) -> None:
        """Render match victory celebration overlay."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 205))
        surface.blit(overlay, (0, 0))

        winner_str = f"PLAYER {winner} WINS!" if winner else "GAME OVER"
        text_surf = self.font_overlay.render(winner_str, True, COLOR_VICTORY)
        surface.blit(
            text_surf,
            (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 60),
        )

        sub_surf = self.font_sub.render("PRESS [SPACE] FOR REMATCH", True, COLOR_TEXT)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, self.height // 2 + 30),
        )
