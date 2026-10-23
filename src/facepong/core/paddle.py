"""Paddle representation and movement dynamics."""

from __future__ import annotations


class Paddle:
    """Represents a player paddle with continuous floating-point physics."""

    def __init__(
        self,
        x: float,
        initial_y: float,
        width: float,
        height: float,
        bounds_height: float,
        speed: float = 700.0,
    ) -> None:
        """Initialize paddle dimensions, position and movement bounds.

        Args:
            x: Fixed horizontal coordinate (top-left X).
            initial_y: Initial top-left Y coordinate.
            width: Paddle width in pixels.
            height: Paddle height in pixels.
            bounds_height: Total vertical arena boundary (screen height).
            speed: Maximum velocity in pixels per second (for keyboard deltas).
        """
        self.x = float(x)
        self.width = float(width)
        self.height = float(height)
        self.bounds_height = float(bounds_height)
        self.speed = float(speed)

        self.min_y = 0.0
        self.max_y = max(0.0, self.bounds_height - self.height)

        self.y = self._clamp(float(initial_y))
        self.target_y: float | None = None

    def _clamp(self, val: float) -> float:
        """Clamp vertical position inside arena bounds."""
        return max(self.min_y, min(val, self.max_y))

    @property
    def center_y(self) -> float:
        """Get center Y coordinate of paddle."""
        return self.y + (self.height / 2.0)

    @property
    def rect(self) -> tuple[float, float, float, float]:
        """Return (x, y, width, height) tuple."""
        return (self.x, self.y, self.width, self.height)

    def set_normalized_position(self, norm_y: float) -> None:
        """Set target paddle position based on normalized coordinate [0.0, 1.0].

        Args:
            norm_y: 0.0 represents top of screen, 1.0 represents bottom.
        """
        clamped_norm = max(0.0, min(norm_y, 1.0))
        # Map [0, 1] to [min_y, max_y]
        self.target_y = self.min_y + (clamped_norm * (self.max_y - self.min_y))

    def move_by_delta(self, dy: float) -> None:
        """Move paddle instantly by offset (used by keyboard inputs)."""
        self.y = self._clamp(self.y + dy)
        self.target_y = None

    def update(self, dt: float) -> None:
        """Update paddle position smoothly towards target position if specified.

        Args:
            dt: Delta time in seconds since last frame.
        """
        if self.target_y is None:
            return

        diff = self.target_y - self.y
        if abs(diff) < 0.5:
            self.y = self.target_y
            return

        # Ultra-responsive kinematic lerp: snaps to target immediately without sluggish delay
        lerp_step = diff * min(1.0, 48.0 * dt)
        self.y = self._clamp(self.y + lerp_step)

    def reset(self) -> None:
        """Reset paddle to vertical center."""
        self.y = self._clamp((self.bounds_height - self.height) / 2.0)
        self.target_y = None
