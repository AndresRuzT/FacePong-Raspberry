"""Exponential Moving Average (EMA) and deadband signal smoothing."""

from __future__ import annotations


class EMASmoother:
    """Exponential Moving Average filter with deadzone noise suppression."""

    def __init__(self, alpha: float = 0.28, deadzone: float = 0.025) -> None:
        """Initialize filter parameters.

        Args:
            alpha: Smoothing factor in range (0.0, 1.0]. Lower values yield
                   smoother output; higher values yield faster response.
            deadzone: Minimal amplitude difference required to trigger an update.
        """
        if not (0.0 < alpha <= 1.0):
            raise ValueError(f"Alpha must be in range (0.0, 1.0], got {alpha}")
        if deadzone < 0.0:
            raise ValueError(f"Deadzone must be non-negative, got {deadzone}")

        self.alpha = float(alpha)
        self.deadzone = float(deadzone)
        self.current_value: float | None = None

    def filter(self, raw_value: float) -> float:
        """Filter incoming raw measurement.

        Args:
            raw_value: New scalar sample.

        Returns:
            Smoothed scalar value.
        """
        if self.current_value is None:
            self.current_value = float(raw_value)
            return self.current_value

        delta = abs(raw_value - self.current_value)
        if delta < self.deadzone:
            return self.current_value

        self.current_value = (self.alpha * float(raw_value)) + (
            (1.0 - self.alpha) * self.current_value
        )
        return self.current_value

    def reset(self) -> None:
        """Clear filter internal memory."""
        self.current_value = None
