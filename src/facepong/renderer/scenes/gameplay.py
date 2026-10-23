"""Gameplay rendering scene with exterior dashboard, framed court, and clean HUD."""

from __future__ import annotations

import pygame

from facepong.config.settings import DebugConfig
from facepong.core.game import Game, GameState
from facepong.renderer.hud import HUD

COLOR_PADDLE_P1 = (0, 220, 255)  # Cyan
COLOR_PADDLE_P2 = (255, 150, 20)  # Amber
COLOR_BALL = (255, 255, 255)  # Pure White
COLOR_VICTORY = (255, 215, 0)  # Gold
COLOR_TEXT = (255, 255, 255)


class GameplayRenderer:
    """Renders active match elements: exterior dashboard, framed arena, and overlays."""

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

        self.font_overlay = pygame.font.SysFont("dejavusans,freesansbold,arial", 52, bold=True)
        self.font_sub = pygame.font.SysFont("dejavusans,arial", 22)

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
        preview_surface: pygame.Surface | None = None,
        show_preview: bool = True,
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
            preview_surface: Pygame Surface with live camera frame and face tracking.
            show_preview: Unused compatibility flag.
        """
        # 1. Top exterior dashboard frame (houses Branding, Telemetry, and Live Camera)
        self.hud.draw_top_dashboard(
            surface=surface,
            p1_detected=p1_detected,
            p2_detected=p2_detected,
            p1_type=p1_type,
            p2_type=p2_type,
            game_fps=game_fps,
            cv_fps=cv_fps,
            preview_surface=preview_surface,
        )

        # 2. Dedicated playing court arena (unobstructed field of play)
        self.hud.draw_court(
            surface=surface,
            arena_x=game.arena_x,
            arena_y=game.arena_y,
            arena_w=game.arena_w,
            arena_h=game.arena_h,
            p1_score=game.score.p1_score,
            p2_score=game.score.p2_score,
        )

        # 3. Paddle 1 (Left - Cyan)
        p1_rect = pygame.Rect(
            int(game.paddle1.x),
            int(game.paddle1.y),
            int(game.paddle1.width),
            int(game.paddle1.height),
        )
        pygame.draw.rect(surface, COLOR_PADDLE_P1, p1_rect, border_radius=6)

        # 4. Paddle 2 (Right - Amber)
        p2_rect = pygame.Rect(
            int(game.paddle2.x),
            int(game.paddle2.y),
            int(game.paddle2.width),
            int(game.paddle2.height),
        )
        pygame.draw.rect(surface, COLOR_PADDLE_P2, p2_rect, border_radius=6)

        # 5. Central Ball
        pygame.draw.circle(
            surface,
            COLOR_BALL,
            (int(game.ball.x), int(game.ball.y)),
            int(game.ball.radius),
        )

        # 6. Bottom Command Shortcuts Bar
        self.hud.draw_footer_help(surface)

        # 7. Pause Overlay
        if game.state == GameState.PAUSED:
            self._draw_pause_overlay(surface)

        # 8. Game Over Overlay
        elif game.state == GameState.GAME_OVER:
            self._draw_game_over_overlay(surface, game.score.winner)

    def _draw_pause_overlay(self, surface: pygame.Surface) -> None:
        """Render pause dialog overlay."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 14, 22, 185))
        surface.blit(overlay, (0, 0))

        text_surf = self.font_overlay.render("PAUSA", True, COLOR_TEXT)
        surface.blit(
            text_surf,
            (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 40),
        )

        sub_surf = self.font_sub.render("PRESIONEN [ESPACIO] PARA CONTINUAR", True, COLOR_PADDLE_P1)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, self.height // 2 + 25),
        )

    def _draw_game_over_overlay(self, surface: pygame.Surface, winner: int | None) -> None:
        """Render match victory celebration overlay."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 14, 22, 210))
        surface.blit(overlay, (0, 0))

        winner_str = f"VICTORIA: JUGADOR {winner}" if winner else "FIN DE PARTIDA"
        winner_color = COLOR_PADDLE_P1 if winner == 1 else COLOR_PADDLE_P2
        text_surf = self.font_overlay.render(winner_str, True, winner_color)
        surface.blit(
            text_surf,
            (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50),
        )

        sub_surf = self.font_sub.render("PRESIONEN [ESPACIO] PARA REVANCHA", True, COLOR_TEXT)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, self.height // 2 + 30),
        )
