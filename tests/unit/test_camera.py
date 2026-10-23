"""Tests for CameraCapture and frame partitioning."""

from unittest.mock import MagicMock

import numpy as np

from facepong.vision.camera import CameraCapture


def test_camera_init() -> None:
    """Verify initialization parameters."""
    cam = CameraCapture(camera_index=0, frame_width=320, frame_height=240, fps=20)
    assert cam.camera_index == 0
    assert cam.frame_width == 320
    assert cam.frame_height == 240
    assert not cam.is_opened()


def test_camera_read_split_mocked() -> None:
    """Verify horizontal partitioning of camera frame into left and right subframes."""
    cam = CameraCapture(camera_index=0, frame_width=320, frame_height=240, fps=20)

    # Mock VideoCapture
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True

    # Dummy BGR frame of size 240x320x3
    dummy_frame = np.ones((240, 320, 3), dtype=np.uint8) * 100
    mock_cap.read.return_value = (True, dummy_frame)

    cam._cap = mock_cap

    p1_frame, p2_frame = cam.read_split_frames()
    assert p1_frame is not None
    assert p2_frame is not None

    # Each half should have width 160 and height 240
    assert p1_frame.shape == (240, 160, 3)
    assert p2_frame.shape == (240, 160, 3)

    cam.release()
    assert cam._cap is None
