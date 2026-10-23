"""Main menu and start screen renderer with live camera preview."""

from __future__ import annotations

import pygame

COLOR_TITLE = (255, 255, 255)
COLOR_SUBTITLE = (140, 160, 185)
COLOR_PROMPT = (90, 200, 250)
COLOR_HINT = (120, 130, 145)
COLOR_BORDER = (60, 75, 95)


class MenuRenderer:
    """Renders academic title screen, player positioning instructions, and live camera preview."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize menu text surfaces."""
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("dejavusans,freesansbold,arial", 60, bold=True)
        self.font_subtitle = pygame.font.SysFont("dejavusans,arial", 20)
        self.font_prompt = pygame.font.SysFont("dejavusans,freesansbold,arial", 24, bold=True)
        self.font_cam_label = pygame.font.SysFont("dejavusans,freesansbold,arial", 16)
        self.font_hint = pygame.font.SysFont("dejavusans,arial", 15)

    def draw(self, surface: pygame.Surface, preview_surface: pygame.Surface | None = None) -> None:
        """Render menu layout with optional live camera preview window."""
        # Main Title
        title_surf = self.font_title.render("FACE PONG", True, COLOR_TITLE)
        surface.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, 28),
        )

        # Subtitle
        sub_text = "Computer Vision Head-Tracking Interface | Raspberry Pi 4"
        sub_surf = self.font_subtitle.render(sub_text, True, COLOR_SUBTITLE)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, 95),
        )

        # Live Camera Alignment Box
        cam_y = 135
        if preview_surface is not None:
            cam_w, cam_h = preview_surface.get_size()
            cam_x = self.width // 2 - cam_w // 2

            # Background and border
            border_rect = pygame.Rect(cam_x - 3, cam_y - 3, cam_w + 6, cam_h + 6)
            pygame.draw.rect(surface, COLOR_BORDER, border_rect, width=2, border_radius=6)

            # Camera feed
            surface.blit(preview_surface, (cam_x, cam_y))

            # Alignment labels above camera
            lbl_p1 = self.font_cam_label.render("<< JUGADOR 1 (Izq)", True, (90, 200, 250))
            lbl_p2 = self.font_cam_label.render("JUGADOR 2 (Der) >>", True, (255, 149, 0))
            surface.blit(lbl_p1, (cam_x + 8, cam_y + 6))
            surface.blit(lbl_p2, (cam_x + cam_w - lbl_p2.get_width() - 8, cam_y + 6))

            prompt_y = cam_y + cam_h + 18
        else:
            prompt_y = 260

        # Start Action Prompt
        prompt_surf = self.font_prompt.render(
            "PRESIONEN [ESPACIO] PARA CALIBRAR Y JUGAR", True, COLOR_PROMPT
        )
        surface.blit(
            prompt_surf,
            (self.width // 2 - prompt_surf.get_width() // 2, prompt_y),
        )

        # Instructions / Help
        instructions = [
            "Ubiquense frente a la camara mirando al frente hasta ver sus recuadros en verde",
            "Muevan o inclinen el rostro arriba / abajo para controlar las paletas",
            "Presionen [C] en cualquier momento para recalibrar el centro del rostro",
            "Teclado de respaldo: [W / S] para Jugador 1  |  [Flechas Arriba / Abajo] para Jugador 2",
            "[Espacio] Pausa  |  [V] Ocultar/Mostrar Camara  |  [R] Reiniciar  |  [Esc] Salir",
        ]

        y_offset = prompt_y + 44
        for line in instructions:
            inst_surf = self.font_hint.render(line, True, COLOR_HINT)
            surface.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, y_offset))
            y_offset += 22
