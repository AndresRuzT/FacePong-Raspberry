"""Head tilt estimation and coordinate mapping."""

from __future__ import annotations

from dataclasses import dataclass

from facepong.vision.smoother import EMASmoother


@dataclass(frozen=True)
class FacialKeypoints:
    """Essential 2D normalized coordinates and bounding box extracted from face detection."""

    forehead_y: float  # Landmark 10 or top of bounding box
    nose_y: float  # Landmark 4 or nose/eye estimate
    chin_y: float  # Landmark 152 or bottom of bounding box
    center_y: float = 0.5  # Vertical center of detected face in subframe [0.0, 1.0]
    bbox: tuple[int, int, int, int] = (0, 0, 0, 0)  # (x, y, w, h) in subframe pixels


class HeadPoseEstimator:
    """Maps vertical facial tilt and pitch to normalized paddle coordinates [0.0, 1.0]."""

    def __init__(
        self,
        neutral_ratio: float = 0.45,
        sensitivity: float = 5.5,
        smoothing_alpha: float = 0.32,
        max_alpha: float = 0.88,
        deadzone: float = 0.008,
        invert: bool = False,
    ) -> None:
        """Initialize head pose estimator.

        Args:
            neutral_ratio: Baseline ratio (nose_y - forehead_y) / face_height
                           when looking directly ahead.
            sensitivity: Gain multiplier scaling facial tilt into arena movement.
            smoothing_alpha: Base filter factor for resting stability.
            max_alpha: High-speed filter factor for zero-latency rapid gestures.
            deadzone: Minimal threshold suppressing rest micro-tremors.
            invert: Invert control direction if desired.
        """
        self.neutral_ratio = float(neutral_ratio)
        self.sensitivity = float(sensitivity)
        self.invert = bool(invert)
        effective_max = max(smoothing_alpha, max_alpha)
        self.smoother = EMASmoother(
            alpha=smoothing_alpha, deadzone=deadzone, max_alpha=effective_max
        )
        self.neutral_y: float | None = 0.5
        self._calibration_samples: list[float] = []

    def calibrate(self) -> None:
        """Request recalibration of the resting neutral position on next frames."""
        self.neutral_y = None
        self._calibration_samples.clear()
        self.smoother.reset()

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

        # Compute vertical geometric pitch ratio
        raw_pitch = (keypoints.nose_y - keypoints.forehead_y) / face_height

        # Pitch delta relative to baseline neutral ratio
        pitch_delta = raw_pitch - self.neutral_ratio

        # Biomechanical compensation:
        # Looking up causes 2D perspective foreshortening and human neck has lower upward range.
        # Apply 1.8x gain boost specifically to upward tilt to equalize up/down physical effort.
        if pitch_delta < 0:
            pitch_delta *= 1.8

        # Blended metric: face center vertical position in frame + compensated pitch
        current_metric = keypoints.center_y + (pitch_delta * 0.65)

        # Baseline calibration: if recalibration requested, calibrate to current posture
        if self.neutral_y is None:
            self._calibration_samples.append(current_metric)
            if len(self._calibration_samples) >= 3:
                self.neutral_y = sum(self._calibration_samples) / len(self._calibration_samples)
            else:
                self.neutral_y = current_metric

        # Deviation relative to calibrated resting baseline
        deviation = current_metric - self.neutral_y

        # Upward motion gain: boost upward deviation so players easily reach top edge
        gain = 1.6 if deviation < 0 else 1.2

        # Map deviation into [0.0, 1.0]: 0.5 is center screen
        target_pos = 0.5 + (deviation * gain * self.sensitivity)

        if self.invert:
            target_pos = 1.0 - target_pos

        clamped = max(0.0, min(target_pos, 1.0))
        return self.smoother.filter(clamped)

    def reset(self) -> None:
        """Reset internal filter state."""
        self.smoother.reset()
        self.neutral_y = 0.5
        self._calibration_samples.clear()
