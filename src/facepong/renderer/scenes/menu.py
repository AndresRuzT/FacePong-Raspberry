"""Main menu and start screen renderer with live camera preview."""

from __future__ import annotations

import pygame

COLOR_TITLE = (255, 255, 255)
COLOR_SUBTITLE = (140, 160, 185)
COLOR_PROMPT = (0, 220, 255)
COLOR_HINT = (130, 145, 165)
COLOR_BORDER = (55, 75, 105)
COLOR_BOX_BG = (18, 24, 34)


class MenuRenderer:
    """Renders academic title screen, player positioning instructions, and live camera preview."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize menu text surfaces."""
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("dejavusans,freesansbold,arial", 56, bold=True)
        self.font_subtitle = pygame.font.SysFont("dejavusans,arial", 18)
        self.font_prompt = pygame.font.SysFont("dejavusans,freesansbold,arial", 22, bold=True)
        self.font_cam_label = pygame.font.SysFont("dejavusans,freesansbold,arial", 14, bold=True)
        self.font_hint = pygame.font.SysFont("dejavusans,arial", 14)
        self.font_status = pygame.font.SysFont("dejavusans,arial", 13)

    def draw(self, surface: pygame.Surface, preview_surface: pygame.Surface | None = None) -> None:
        """Render menu layout with optional live camera preview window."""
        # Main Title
        title_surf = self.font_title.render("FACE PONG", True, COLOR_TITLE)
        surface.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, 24),
        )

        # Subtitle
        sub_text = "Sistema Interactivo HCI por Visión Artificial | Raspberry Pi 4"
        sub_surf = self.font_subtitle.render(sub_text, True, COLOR_SUBTITLE)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, 86),
        )

        # Live Camera Alignment Box
        cam_target_w = 320
        cam_target_h = 240
        cam_x = self.width // 2 - cam_target_w // 2
        cam_y = 124

        border_rect = pygame.Rect(cam_x - 3, cam_y - 3, cam_target_w + 6, cam_target_h + 6)
        pygame.draw.rect(surface, COLOR_BOX_BG, border_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BORDER, border_rect, width=2, border_radius=8)

        if preview_surface is not None:
            scaled_cam = pygame.transform.smoothscale(preview_surface, (cam_target_w, cam_target_h))
            surface.blit(scaled_cam, (cam_x, cam_y))

            # Alignment labels
            lbl_p1 = self.font_cam_label.render("<< JUGADOR 1 (Izq)", True, (0, 220, 255))
            lbl_p2 = self.font_cam_label.render("JUGADOR 2 (Der) >>", True, (255, 150, 20))
            surface.blit(lbl_p1, (cam_x + 8, cam_y + 8))
            surface.blit(lbl_p2, (cam_x + cam_target_w - lbl_p2.get_width() - 8, cam_y + 8))
        else:
            # Elegant camera initializing placeholder
            load_title = self.font_cam_label.render(
                "INICIALIZANDO SENSOR DE VISIÓN...", True, (0, 220, 255)
            )
            surface.blit(
                load_title,
                (cam_x + (cam_target_w // 2) - (load_title.get_width() // 2), cam_y + 90),
            )
            load_sub = self.font_status.render(
                "Conectando cámara USB y cargando modelos...", True, COLOR_HINT
            )
            surface.blit(
                load_sub,
                (cam_x + (cam_target_w // 2) - (load_sub.get_width() // 2), cam_y + 120),
            )

        # Start Action Prompt
        prompt_y = cam_y + cam_target_h + 20
        prompt_surf = self.font_prompt.render(
            "PRESIONEN [ESPACIO] PARA CALIBRAR Y COMENZAR", True, COLOR_PROMPT
        )
        surface.blit(
            prompt_surf,
            (self.width // 2 - prompt_surf.get_width() // 2, prompt_y),
        )

        # Instructions / Help
        instructions = [
            "Ubíquense frente a la cámara mirando al frente hasta ver sus recuadros en verde",
            "Muevan o inclinen el rostro arriba / abajo para controlar las paletas con fluidez",
            "Presionen [C] en cualquier momento de la partida para recalibrar el centro facial",
            "Modo teclado: [W / S] para Jugador 1  |  [Flechas Arriba / Abajo] para Jugador 2",
            "[Espacio] Pausa / Continuar  |  [R] Reiniciar  |  [Esc] Salir",
        ]

        y_offset = prompt_y + 42
        for line in instructions:
            inst_surf = self.font_hint.render(line, True, COLOR_HINT)
            surface.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, y_offset))
            y_offset += 22
