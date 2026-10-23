"""Camera capture and dual-player frame partitioning."""

from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraCapture:
    """Wrapper around OpenCV VideoCapture with frame splitting for 2 players."""

    def __init__(
        self,
        camera_index: int = 0,
        frame_width: int = 320,
        frame_height: int = 240,
        fps: int = 20,
    ) -> None:
        """Initialize camera capture.

        Args:
            camera_index: V4L2 device index (0 for /dev/video0).
            frame_width: Target capture width in pixels.
            frame_height: Target capture height in pixels.
            fps: Target capture framerate.
        """
        self.camera_index = camera_index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.target_fps = fps
        self._cap: cv2.VideoCapture | None = None

    def start(self) -> bool:
        """Open camera hardware device and configure properties."""
        try:
            # Prefer V4L2 on Linux for lower latency and direct driver access
            self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            if not self._cap.isOpened():
                self._cap = cv2.VideoCapture(self.camera_index)

            if not self._cap.isOpened():
                logger.warning("Could not open camera device %d.", self.camera_index)
                return False

            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self._cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            return True
        except Exception as exc:
            logger.error("Error opening camera device: %s", exc)
            return False

    def is_opened(self) -> bool:
        """Check whether camera device is open."""
        return self._cap is not None and self._cap.isOpened()

    def read_split_frames(
        self,
    ) -> tuple[np.ndarray[Any, Any] | None, np.ndarray[Any, Any] | None]:
        """Capture one frame and partition horizontally for Player 1 and Player 2.

        Returns:
            Tuple of (left_rgb_frame, right_rgb_frame) or (None, None) on failure.
        """
        if self._cap is None or not self._cap.isOpened():
            return None, None

        ret, frame = self._cap.read()
        if not ret or frame is None:
            return None, None

        # Convert to RGB (MediaPipe requirement)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, width, _ = rgb.shape
        mid = width // 2

        # Left half = Player 1, Right half = Player 2
        # As Player 1 sits on the left side of the screen/camera
        left_subframe = np.ascontiguousarray(rgb[:, :mid])
        right_subframe = np.ascontiguousarray(rgb[:, mid:])

        return left_subframe, right_subframe

    def release(self) -> None:
        """Release camera resource."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
