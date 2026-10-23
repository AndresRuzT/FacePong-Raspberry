"""Tests for FaceMeshDetector dual backends."""

from unittest.mock import MagicMock

import numpy as np

from facepong.vision.face_mesh import FaceMeshDetector


def test_face_mesh_initialization() -> None:
    """Verify detector initialization and availability."""
    detector = FaceMeshDetector(model_complexity=0, refine_landmarks=False)
    assert detector is not None
    assert detector.is_available is True
    detector.close()


def test_face_mesh_mediapipe_flow() -> None:
    """Verify landmarks extraction when MediaPipe returns landmarks."""
    detector = FaceMeshDetector()

    mock_mp = MagicMock()
    mock_landmark = [MagicMock(x=0.1, y=0.1 * i) for i in range(468)]
    mock_result = MagicMock()
    mock_result.multi_face_landmarks = [MagicMock(landmark=mock_landmark)]
    mock_mp.process.return_value = mock_result

    detector._mp_mesh = mock_mp

    dummy_frame = np.zeros((240, 160, 3), dtype=np.uint8)
    keypoints = detector.process_frame(dummy_frame)

    assert keypoints is not None
    assert keypoints.forehead_y == mock_landmark[10].y
    assert keypoints.nose_y == mock_landmark[4].y
    assert keypoints.chin_y == mock_landmark[152].y


def test_face_mesh_opencv_fallback() -> None:
    """Verify extraction when falling back to OpenCV Haar cascade."""
    detector = FaceMeshDetector()
    detector._mp_mesh = None  # Force OpenCV cascade path

    mock_cascade = MagicMock()
    # (x, y, w, h)
    mock_cascade.detectMultiScale.return_value = np.array([[20, 30, 60, 80]])
    mock_cascade.empty.return_value = False

    detector._cv_cascade = mock_cascade

    dummy_frame = np.zeros((200, 200, 3), dtype=np.uint8)
    keypoints = detector.process_frame(dummy_frame)

    assert keypoints is not None
    # forehead = 30 / 200 = 0.15
    assert keypoints.forehead_y == 0.15
    # chin = (30 + 80) / 200 = 0.55
    assert keypoints.chin_y == 0.55
