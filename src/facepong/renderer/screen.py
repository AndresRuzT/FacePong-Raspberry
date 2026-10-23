"""Pygame display and rendering surface configuration."""

from __future__ import annotations

import logging

import pygame

from facepong.config.settings import DisplayConfig

logger = logging.getLogger(__name__)


class ScreenManager:
    """Manages Pygame display context, resolutions, and frame buffer flips."""

    def __init__(self, config: DisplayConfig) -> None:
        """Initialize display context.

        Args:
            config: Display settings.
        """
        self.config = config
        self.width = config.width
        self.height = config.height
        self._surface: pygame.Surface | None = None

    def initialize(self) -> pygame.Surface:
        """Initialize Pygame video subsystem and create window surface.

        Returns:
            Main screen surface for rendering.
        """
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        flags = pygame.DOUBLEBUF
        if self.config.fullscreen:
            flags |= pygame.FULLSCREEN

        self._surface = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self.config.title)
        logger.info(
            "Display initialized: %dx%d (fullscreen=%s)",
            self.width,
            self.height,
            self.config.fullscreen,
        )
        return self._surface

    @property
    def surface(self) -> pygame.Surface:
        """Return initialized display surface."""
        if self._surface is None:
            raise RuntimeError("Screen surface accessed prior to initialize()")
        return self._surface

    def clear(self, color: tuple[int, int, int] = (15, 17, 23)) -> None:
        """Clear screen with background color (deep dark academic slate)."""
        if self._surface is not None:
            self._surface.fill(color)

    def flip(self) -> None:
        """Swap frame buffers."""
        pygame.display.flip()
