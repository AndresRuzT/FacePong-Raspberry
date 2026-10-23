"""Tests for HeadPoseEstimator ratio mapping."""

from facepong.vision.head_pose import FacialKeypoints, HeadPoseEstimator


def test_head_pose_none_handling() -> None:
    """None keypoints should return None safely."""
    estimator = HeadPoseEstimator()
    assert estimator.estimate_vertical_position(None) is None


def test_head_pose_invalid_height() -> None:
    """Zero or negative face height returns None."""
    estimator = HeadPoseEstimator()
    kp = FacialKeypoints(forehead_y=0.5, nose_y=0.5, chin_y=0.5)
    assert estimator.estimate_vertical_position(kp) is None


def test_head_pose_neutral_and_tilt() -> None:
    """Neutral ratio produces center screen (0.5); tilting alters position."""
    estimator = HeadPoseEstimator(
        neutral_ratio=0.45, sensitivity=2.0, smoothing_alpha=1.0, deadzone=0.0
    )

    # Perfect neutral pose: forehead=0.2, chin=0.8, height=0.6, nose=0.2 + 0.45*0.6 = 0.47
    neutral_kp = FacialKeypoints(forehead_y=0.2, nose_y=0.47, chin_y=0.8)
    pos = estimator.estimate_vertical_position(neutral_kp)
    assert pos is not None
    assert abs(pos - 0.5) < 0.01

    # Tilt downward: nose drops lower towards chin
    tilt_down_kp = FacialKeypoints(forehead_y=0.2, nose_y=0.53, chin_y=0.8)
    down_pos = estimator.estimate_vertical_position(tilt_down_kp)
    assert down_pos is not None
    assert down_pos > 0.5  # Moving down

    # Tilt upward: nose moves closer to forehead
    tilt_up_kp = FacialKeypoints(forehead_y=0.2, nose_y=0.40, chin_y=0.8)
    up_pos = estimator.estimate_vertical_position(tilt_up_kp)
    assert up_pos is not None
    assert up_pos < 0.5  # Moving up


def test_head_pose_inversion() -> None:
    """Verify inversion reverses the direction mapping."""
    estimator = HeadPoseEstimator(
        neutral_ratio=0.45, sensitivity=2.0, smoothing_alpha=1.0, deadzone=0.0, invert=True
    )
    tilt_down_kp = FacialKeypoints(forehead_y=0.2, nose_y=0.53, chin_y=0.8)
    pos = estimator.estimate_vertical_position(tilt_down_kp)
    assert pos is not None
    assert pos < 0.5  # Inverted downward tilt maps to upper coordinate
