"""Heads-Up Display (HUD) and exterior frame dashboard rendering."""

from __future__ import annotations

import pygame

from facepong.config.settings import DebugConfig

# Color Palette (High-contrast, retro-academic HCI theme)
COLOR_BG_PANEL = (20, 25, 36)
COLOR_BORDER_PANEL = (42, 54, 76)
COLOR_COURT_BG = (14, 18, 27)
COLOR_COURT_BORDER = (55, 72, 100)
COLOR_NET = (40, 52, 72)

COLOR_P1 = (0, 220, 255)  # Electric Cyan
COLOR_P2 = (255, 150, 20)  # Sunburst Amber
COLOR_TEXT_PRIMARY = (240, 245, 250)
COLOR_TEXT_MUTED = (130, 145, 165)
COLOR_STATUS_ACTIVE = (50, 215, 75)  # Green
COLOR_STATUS_INACTIVE = (255, 69, 58)  # Red


class HUD:
    """Renders exterior dashboard frame, match scoreboard, and court geometry."""

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

        # Academic fonts
        self.font_logo = pygame.font.SysFont("dejavusans,freesansbold,arial", 26, bold=True)
        self.font_sub = pygame.font.SysFont("dejavusans,arial", 12)
        self.font_score = pygame.font.SysFont("dejavusans,freesansbold,arial", 68, bold=True)
        self.font_card = pygame.font.SysFont("dejavusans,freesansbold,arial", 13, bold=True)
        self.font_info = pygame.font.SysFont("dejavusans,arial", 13)
        self.font_footer = pygame.font.SysFont("dejavusans,arial", 13)

    def draw_top_dashboard(
        self,
        surface: pygame.Surface,
        p1_detected: bool,
        p2_detected: bool,
        p1_type: str,
        p2_type: str,
        game_fps: float,
        cv_fps: float,
        preview_surface: pygame.Surface | None = None,
    ) -> None:
        """Render upper exterior frame containing branding, live camera, and player cards."""
        panel_rect = pygame.Rect(18, 8, self.width - 36, 130)
        pygame.draw.rect(surface, COLOR_BG_PANEL, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER_PANEL, panel_rect, width=2, border_radius=8)

        # 1. Left Branding Block
        title_surf = self.font_logo.render("FACEPONG", True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surf, (36, 18))

        sub_surf = self.font_sub.render("HCI RESEARCH LAB | RPi 4", True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (36, 48))

        # Player 1 Badge
        p1_badge_rect = pygame.Rect(36, 72, 210, 48)
        pygame.draw.rect(surface, (26, 32, 46), p1_badge_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_P1, p1_badge_rect, width=1, border_radius=6)

        p1_title = self.font_card.render(f"P1 [{p1_type.upper()}]", True, COLOR_P1)
        surface.blit(p1_title, (48, 78))

        led_p1 = COLOR_STATUS_ACTIVE if p1_detected else COLOR_STATUS_INACTIVE
        pygame.draw.circle(surface, led_p1, (52, 104), 4)
        status_p1_text = "CONECTADO" if p1_detected else "BUSCANDO..."
        p1_status_surf = self.font_sub.render(status_p1_text, True, COLOR_TEXT_MUTED)
        surface.blit(p1_status_surf, (64, 97))

        # 2. Center: Camera Box in Header Frame
        cam_target_w = 200
        cam_target_h = 114
        cam_x = (self.width // 2) - (cam_target_w // 2)
        cam_y = 16

        cam_bezel = pygame.Rect(cam_x - 3, cam_y - 3, cam_target_w + 6, cam_target_h + 6)
        pygame.draw.rect(surface, (12, 16, 24), cam_bezel, border_radius=6)
        pygame.draw.rect(surface, (60, 80, 110), cam_bezel, width=2, border_radius=6)

        if preview_surface is not None:
            scaled_cam = pygame.transform.smoothscale(preview_surface, (cam_target_w, cam_target_h))
            surface.blit(scaled_cam, (cam_x, cam_y))
        else:
            # Camera initializing placeholder
            load_txt = self.font_sub.render("INICIANDO CÁMARA...", True, (100, 130, 170))
            surface.blit(
                load_txt,
                (cam_x + (cam_target_w // 2) - (load_txt.get_width() // 2), cam_y + 48),
            )

        # 3. Right Block: Player 2 Badge & Telemetry
        p2_badge_rect = pygame.Rect(self.width - 246, 72, 210, 48)
        pygame.draw.rect(surface, (26, 32, 46), p2_badge_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_P2, p2_badge_rect, width=1, border_radius=6)

        p2_title = self.font_card.render(f"P2 [{p2_type.upper()}]", True, COLOR_P2)
        surface.blit(p2_title, (self.width - 234, 78))

        led_p2 = COLOR_STATUS_ACTIVE if p2_detected else COLOR_STATUS_INACTIVE
        pygame.draw.circle(surface, led_p2, (self.width - 230, 104), 4)
        status_p2_text = "CONECTADO" if p2_detected else "BUSCANDO..."
        p2_status_surf = self.font_sub.render(status_p2_text, True, COLOR_TEXT_MUTED)
        surface.blit(p2_status_surf, (self.width - 218, 97))

        rule_txt = self.font_card.render("PRIMERO A 5 PUNTOS", True, COLOR_TEXT_MUTED)
        surface.blit(rule_txt, (self.width - 36 - rule_txt.get_width(), 20))

        fps_txt = self.font_info.render(
            f"GAME: {game_fps:4.1f} FPS | CV: {cv_fps:4.1f} FPS", True, (110, 130, 155)
        )
        surface.blit(fps_txt, (self.width - 36 - fps_txt.get_width(), 44))

    def draw_court(
        self,
        surface: pygame.Surface,
        arena_x: float,
        arena_y: float,
        arena_w: float,
        arena_h: float,
        p1_score: int,
        p2_score: int,
    ) -> None:
        """Render playing arena boundary, center dividing net, and scores."""
        court_rect = pygame.Rect(int(arena_x), int(arena_y), int(arena_w), int(arena_h))
        pygame.draw.rect(surface, COLOR_COURT_BG, court_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_COURT_BORDER, court_rect, width=3, border_radius=8)

        # Dashed net
        center_x = int(arena_x + (arena_w / 2.0))
        net_y = int(arena_y + 10)
        net_end_y = int(arena_y + arena_h - 10)
        while net_y < net_end_y:
            pygame.draw.line(
                surface,
                COLOR_NET,
                (center_x, net_y),
                (center_x, min(net_y + 16, net_end_y)),
                width=3,
            )
            net_y += 26

        # Scoreboard rendered inside court
        p1_surf = self.font_score.render(str(p1_score), True, COLOR_P1)
        surface.blit(p1_surf, (center_x - 140 - (p1_surf.get_width() // 2), int(arena_y + 24)))

        p2_surf = self.font_score.render(str(p2_score), True, COLOR_P2)
        surface.blit(p2_surf, (center_x + 140 - (p2_surf.get_width() // 2), int(arena_y + 24)))

    def draw_footer_help(self, surface: pygame.Surface) -> None:
        """Render quick control shortcut bar at bottom of window."""
        hints = "[ESPACIO] Iniciar / Pausa  |  [C] Recalibrar Centro Facial  |  [R] Reiniciar Partida  |  [ESC] Salir"
        hint_surf = self.font_footer.render(hints, True, COLOR_TEXT_MUTED)
        surface.blit(
            hint_surf,
            (self.width // 2 - hint_surf.get_width() // 2, self.height - 22),
        )
