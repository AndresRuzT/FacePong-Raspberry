"""Main menu and start screen renderer."""

from __future__ import annotations

import pygame

COLOR_TITLE = (255, 255, 255)
COLOR_SUBTITLE = (140, 160, 185)
COLOR_PROMPT = (90, 200, 250)
COLOR_HINT = (100, 110, 125)


class MenuRenderer:
    """Renders academic title screen and instructions."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize menu text surfaces."""
        self.width = width
        self.height = height
        self.font_title = pygame.font.SysFont("dejavusans,freesansbold,arial", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("dejavusans,arial", 22)
        self.font_prompt = pygame.font.SysFont("dejavusans,freesansbold,arial", 26, bold=True)
        self.font_hint = pygame.font.SysFont("dejavusans,arial", 16)

    def draw(self, surface: pygame.Surface) -> None:
        """Render menu layout."""
        # Main Title
        title_surf = self.font_title.render("FACE PONG", True, COLOR_TITLE)
        surface.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, self.height // 3 - 60),
        )

        # Subtitle
        sub_text = "Computer Vision Head-Tracking Interface | Raspberry Pi 4"
        sub_surf = self.font_subtitle.render(sub_text, True, COLOR_SUBTITLE)
        surface.blit(
            sub_surf,
            (self.width // 2 - sub_surf.get_width() // 2, self.height // 3 + 30),
        )

        # Start Action Prompt
        prompt_surf = self.font_prompt.render("PRESS [SPACE] TO START MATCH", True, COLOR_PROMPT)
        surface.blit(
            prompt_surf,
            (self.width // 2 - prompt_surf.get_width() // 2, (self.height * 2) // 3 - 20),
        )

        # Instructions / Help
        instructions = [
            "Tilt head up / down to guide paddles in real time",
            "Player 1 (Left) & Player 2 (Right) sit side-by-side facing camera",
            "Keyboard fallback: [W/S] for P1  |  [Up/Down Arrows] for P2",
            "[Space] to Pause  |  [R] to Restart  |  [Esc] to Exit",
        ]

        y_offset = (self.height * 2) // 3 + 45
        for line in instructions:
            inst_surf = self.font_hint.render(line, True, COLOR_HINT)
            surface.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, y_offset))
            y_offset += 24
