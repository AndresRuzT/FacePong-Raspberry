"""Abstract base class for input adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod


class InputAdapter(ABC):
    """Abstract interface decoupling input sources from paddle kinematics."""

    @abstractmethod
    def get_normalized_position(self) -> float | None:
        """Get absolute target position in range [0.0, 1.0].

        Returns:
            Float in [0.0, 1.0] (0 = top, 1 = bottom), or None if using relative deltas.
        """
        ...

    @abstractmethod
    def get_delta_y(self, dt: float) -> float:
        """Get relative displacement in pixels for current frame.

        Args:
            dt: Delta time in seconds.

        Returns:
            Displacement offset in pixels.
        """
        ...

    @abstractmethod
    def is_detected(self) -> bool:
        """Return True if the input source is actively connected/detected."""
        ...

    def update(self, dt: float) -> None:
        """Optional frame tick update for internal adapter state."""
        return None
