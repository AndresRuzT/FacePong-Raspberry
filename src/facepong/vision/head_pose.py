"""Head tilt estimation and coordinate mapping."""

from __future__ import annotations

from dataclasses import dataclass

from facepong.vision.smoother import EMASmoother


@dataclass(frozen=True)
class FacialKeypoints:
    """Essential 2D normalized coordinates extracted from face mesh."""

    forehead_y: float  # Landmark 10
    nose_y: float  # Landmark 4
    chin_y: float  # Landmark 152


class HeadPoseEstimator:
    """Maps vertical facial tilt and pitch to normalized paddle coordinates [0.0, 1.0]."""

    def __init__(
        self,
        neutral_ratio: float = 0.45,
        sensitivity: float = 3.2,
        smoothing_alpha: float = 0.28,
        deadzone: float = 0.025,
        invert: bool = False,
    ) -> None:
        """Initialize head pose estimator.

        Args:
            neutral_ratio: Baseline ratio (nose_y - forehead_y) / face_height
                           when looking directly ahead.
            sensitivity: Gain multiplier scaling facial tilt into arena movement.
            smoothing_alpha: Filter factor for output EMA smoother.
            deadzone: Neutral deadzone threshold suppressing rest micro-tremors.
            invert: Invert control direction if desired.
        """
        self.neutral_ratio = float(neutral_ratio)
        self.sensitivity = float(sensitivity)
        self.invert = bool(invert)
        self.smoother = EMASmoother(alpha=smoothing_alpha, deadzone=deadzone)

    def estimate_vertical_position(self, keypoints: FacialKeypoints | None) -> float | None:
        """Calculate normalized vertical position from facial landmarks.

        Args:
            keypoints: Facial keypoints, or None if no face is detected.

        Returns:
            Normalized vertical arena position [0.0, 1.0], or None if no face detected.
        """
        if keypoints is None:
            return None

        face_height = keypoints.chin_y - keypoints.forehead_y
        if face_height <= 0.01:
            return None

        # Compute vertical geometric ratio
        raw_ratio = (keypoints.nose_y - keypoints.forehead_y) / face_height

        # Calculate deviation from resting neutral angle
        deviation = raw_ratio - self.neutral_ratio

        # Map deviation into [0.0, 1.0]: 0.5 is center screen
        # When tilting down: nose moves towards chin -> raw_ratio increases -> target moves down
        # When tilting up: nose moves towards forehead -> raw_ratio decreases -> target moves up
        target_pos = 0.5 + (deviation * self.sensitivity)

        if self.invert:
            target_pos = 1.0 - target_pos

        clamped = max(0.0, min(target_pos, 1.0))
        return self.smoother.filter(clamped)

    def reset(self) -> None:
        """Reset internal filter state."""
        self.smoother.reset()
