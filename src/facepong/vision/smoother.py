"""Exponential Moving Average (EMA) and adaptive signal smoothing."""

from __future__ import annotations


class EMASmoother:
    """Speed-adaptive Exponential Moving Average filter for low jitter and zero lag."""

    def __init__(
        self,
        alpha: float = 0.30,
        deadzone: float = 0.008,
        max_alpha: float | None = None,
    ) -> None:
        """Initialize filter parameters.

        Args:
            alpha: Base smoothing factor in range (0.0, 1.0]. Used during resting posture.
            deadzone: Minimal amplitude difference required to trigger an update.
            max_alpha: Maximum smoothing factor achieved during fast intentional movements.
                       If None, defaults to base alpha (standard fixed EMA).
        """
        if not (0.0 < alpha <= 1.0):
            raise ValueError(f"Alpha must be in range (0.0, 1.0], got {alpha}")
        if deadzone < 0.0:
            raise ValueError(f"Deadzone must be non-negative, got {deadzone}")

        self.alpha = float(alpha)
        self.deadzone = float(deadzone)
        self.max_alpha = float(max_alpha) if max_alpha is not None else self.alpha

        if not (self.alpha <= self.max_alpha <= 1.0):
            raise ValueError(
                f"max_alpha must be in range [{self.alpha}, 1.0], got {self.max_alpha}"
            )

        self.current_value: float | None = None

    def filter(self, raw_value: float) -> float:
        """Filter incoming raw measurement with speed-dependent responsiveness.

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

        # Speed-responsive alpha: smoothly transitions from base alpha (resting)
        # to max_alpha (fast movements), eliminating latency on rapid head gestures.
        if self.max_alpha > self.alpha:
            speed_ratio = min(1.0, delta / 0.04)
            dynamic_alpha = self.alpha + ((self.max_alpha - self.alpha) * speed_ratio)
        else:
            dynamic_alpha = self.alpha

        self.current_value = (dynamic_alpha * float(raw_value)) + (
            (1.0 - dynamic_alpha) * self.current_value
        )
        return self.current_value

    def reset(self) -> None:
        """Clear filter internal memory."""
        self.current_value = None
