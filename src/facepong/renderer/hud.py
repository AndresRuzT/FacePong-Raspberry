"""Heads-Up Display (HUD) rendering and match telemetry."""

from __future__ import annotations

import pygame

from facepong.config.settings import DebugConfig

# Color Palette (High-contrast, retro-academic theme)
COLOR_TEXT_PRIMARY = (235, 240, 245)
COLOR_TEXT_MUTED = (120, 130, 145)
COLOR_NET = (45, 52, 64)
COLOR_STATUS_ACTIVE = (50, 215, 75)  # Vibrant Green
COLOR_STATUS_INACTIVE = (255, 69, 58)  # Alert Red


class HUD:
    """Renders scores, field dividing line, tracking indicators, and FPS telemetry."""

    def __init__(self, screen_width: int, screen_height: int, debug_config: DebugConfig) -> None:
        """Initialize HUD fonts and dimensions.

        Args:
            screen_width: Viewport width.
            screen_height: Viewport height.
            debug_config: Debug and telemetry configuration.
        """
        self.width = screen_width
        self.height = screen_height
        self.debug = debug_config

        # Use system sans fonts with graceful fallbacks
        self.font_score = pygame.font.SysFont("dejavusans,freesansbold,arial", 64, bold=True)
        self.font_info = pygame.font.SysFont("dejavusans,arial", 18)
        self.font_telemetry = pygame.font.SysFont("monospace,courier", 14)

    def draw_net(self, surface: pygame.Surface) -> None:
        """Draw dashed center dividing line."""
        center_x = self.width // 2
        segment_height = 14
        segment_gap = 10
        y = 0
        while y < self.height:
            pygame.draw.line(
                surface,
                COLOR_NET,
                (center_x, y),
                (center_x, min(y + segment_height, self.height)),
                width=3,
            )
            y += segment_height + segment_gap

    def draw_scores(self, surface: pygame.Surface, p1_score: int, p2_score: int) -> None:
        """Render player scores prominently on their respective court sides."""
        # Player 1 (Left)
        p1_surf = self.font_score.render(str(p1_score), True, COLOR_TEXT_PRIMARY)
        surface.blit(p1_surf, (self.width // 4 - p1_surf.get_width() // 2, 40))

        # Player 2 (Right)
        p2_surf = self.font_score.render(str(p2_score), True, COLOR_TEXT_PRIMARY)
        surface.blit(p2_surf, ((self.width * 3) // 4 - p2_surf.get_width() // 2, 40))

    def draw_player_status(
        self,
        surface: pygame.Surface,
        p1_detected: bool,
        p2_detected: bool,
        p1_type: str,
        p2_type: str,
    ) -> None:
        """Draw connection and face tracking indicators for each player."""
        if not self.debug.show_detection_status:
            return

        # Player 1 indicator (Top-Left)
        p1_color = COLOR_STATUS_ACTIVE if p1_detected else COLOR_STATUS_INACTIVE
        pygame.draw.circle(surface, p1_color, (30, 30), 6)
        label_p1 = f"P1 [{p1_type.upper()}]: {'TRACKING' if p1_detected else 'SEARCHING'}"
        p1_text = self.font_info.render(label_p1, True, COLOR_TEXT_MUTED)
        surface.blit(p1_text, (45, 21))

        # Player 2 indicator (Top-Right)
        p2_color = COLOR_STATUS_ACTIVE if p2_detected else COLOR_STATUS_INACTIVE
        label_p2 = f"P2 [{p2_type.upper()}]: {'TRACKING' if p2_detected else 'SEARCHING'}"
        p2_text = self.font_info.render(label_p2, True, COLOR_TEXT_MUTED)
        p2_x = self.width - 45 - p2_text.get_width()
        surface.blit(p2_text, (p2_x, 21))
        pygame.draw.circle(surface, p2_color, (self.width - 30, 30), 6)

    def draw_telemetry(self, surface: pygame.Surface, game_fps: float, cv_fps: float) -> None:
        """Render diagnostic framerates in bottom footer."""
        if not self.debug.show_fps:
            return

        text = f"GAME: {game_fps:4.1f} FPS | CV: {cv_fps:4.1f} FPS"
        telem_surf = self.font_telemetry.render(text, True, COLOR_TEXT_MUTED)
        surface.blit(telem_surf, (self.width // 2 - telem_surf.get_width() // 2, self.height - 24))
