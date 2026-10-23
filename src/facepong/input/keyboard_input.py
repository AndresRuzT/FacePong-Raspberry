"""Keyboard fallback input adapter for desktop testing and accessibility."""

from __future__ import annotations

import pygame

from facepong.input.base import InputAdapter


class KeyboardInputAdapter(InputAdapter):
    """Input adapter handling keyboard directional strokes."""

    def __init__(self, key_up: int, key_down: int, speed: float = 700.0) -> None:
        """Initialize keyboard adapter.

        Args:
            key_up: Pygame key constant for upward displacement (e.g. pygame.K_w).
            key_down: Pygame key constant for downward displacement (e.g. pygame.K_s).
            speed: Velocity in pixels per second.
        """
        self.key_up = key_up
        self.key_down = key_down
        self.speed = float(speed)
        self.up_pressed = False
        self.down_pressed = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process keyboard down/up events."""
        if event.type == pygame.KEYDOWN:
            if event.key == self.key_up:
                self.up_pressed = True
            elif event.key == self.key_down:
                self.down_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key == self.key_up:
                self.up_pressed = False
            elif event.key == self.key_down:
                self.down_pressed = False

    def get_normalized_position(self) -> float | None:
        """Keyboard operates on relative deltas rather than absolute positions."""
        return None

    def get_delta_y(self, dt: float) -> float:
        """Calculate displacement for elapsed delta time."""
        delta = 0.0
        if self.up_pressed:
            delta -= self.speed * dt
        if self.down_pressed:
            delta += self.speed * dt
        return delta

    def is_detected(self) -> bool:
        """Keyboard is always available."""
        return True
