"""Computer vision face tracking input adapter."""

from __future__ import annotations

from facepong.input.base import InputAdapter


class FaceInputAdapter(InputAdapter):
    """Input adapter receiving target paddle positions from CV facial tracking."""

    def __init__(self, player_id: int = 1) -> None:
        """Initialize adapter for specified player.

        Args:
            player_id: 1 for Player 1, 2 for Player 2.
        """
        self.player_id = player_id
        self._current_pos: float | None = 0.5
        self._detected: bool = False

    def update_from_vision(self, position: float | None, detected: bool) -> None:
        """Update tracking state from latest CV worker sample.

        Args:
            position: Normalized vertical coordinate [0.0, 1.0], or None.
            detected: Whether a face is currently detected and tracked.
        """
        self._detected = detected
        if position is not None:
            self._current_pos = position

    def get_normalized_position(self) -> float | None:
        """Return the target normalized vertical position."""
        return self._current_pos

    def get_delta_y(self, dt: float) -> float:
        """Face adapter operates via absolute positioning, not relative steps."""
        return 0.0

    def is_detected(self) -> bool:
        """Return whether player's face is currently tracked."""
        return self._detected
