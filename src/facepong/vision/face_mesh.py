"""Face tracking and keypoint detector with dual MediaPipe and OpenCV backends."""

from __future__ import annotations

import contextlib
import logging
from typing import Any

import cv2
import numpy as np

from facepong.vision.head_pose import FacialKeypoints

logger = logging.getLogger(__name__)

LANDMARK_FOREHEAD = 10
LANDMARK_NOSE = 4
LANDMARK_CHIN = 152


class FaceMeshDetector:
    """Robust face detector utilizing MediaPipe when available, with OpenCV cascade fallback."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 0,
        refine_landmarks: bool = False,
    ) -> None:
        """Initialize detector.

        Args:
            min_detection_confidence: Minimum detection confidence threshold.
            min_tracking_confidence: Minimum landmark tracking confidence.
            model_complexity: 0 for Lite (ARM NEON optimized), 1 for Full.
            refine_landmarks: False disables iris tracking to minimize CPU overhead.
        """
        self._mp_mesh: Any | None = None
        self._cv_cascade: cv2.CascadeClassifier | None = None

        # Attempt to initialize MediaPipe FaceMesh
        try:
            import mediapipe as mp

            if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
                self._mp_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=refine_landmarks,
                    model_complexity=model_complexity,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                )
        except Exception as exc:
            logger.debug("MediaPipe FaceMesh not loaded: %s. Using OpenCV backend.", exc)

        # Initialize high-performance OpenCV Haar Cascade backend
        try:
            cv_data = getattr(cv2, "data", None)
            haarcascades_dir = getattr(cv_data, "haarcascades", "") if cv_data is not None else ""
            face_xml = haarcascades_dir + "haarcascade_frontalface_default.xml"
            self._cv_cascade = cv2.CascadeClassifier(face_xml)
        except Exception as exc:
            logger.warning("Failed to initialize OpenCV Haar cascade: %s", exc)

    @property
    def is_available(self) -> bool:
        """Return True if any detection backend is operational."""
        return self._mp_mesh is not None or (
            self._cv_cascade is not None and not self._cv_cascade.empty()
        )

    def process_frame(self, rgb_frame: np.ndarray[Any, Any]) -> FacialKeypoints | None:
        """Process RGB frame and extract essential vertical keypoints and bounding box.

        Args:
            rgb_frame: RGB numpy array representing sub-frame.

        Returns:
            FacialKeypoints instance if a face is detected, None otherwise.
        """
        if rgb_frame is None or rgb_frame.size == 0:
            return None

        # 1. Try MediaPipe FaceMesh if active
        if self._mp_mesh is not None:
            try:
                results = self._mp_mesh.process(rgb_frame)
                if results and results.multi_face_landmarks:
                    lm = results.multi_face_landmarks[0].landmark
                    forehead_y = float(lm[LANDMARK_FOREHEAD].y)
                    nose_y = float(lm[LANDMARK_NOSE].y)
                    chin_y = float(lm[LANDMARK_CHIN].y)
                    center_y = (forehead_y + chin_y) / 2.0

                    h, w = rgb_frame.shape[:2]
                    all_x = [p.x for p in lm]
                    all_y = [p.y for p in lm]
                    fx = int(min(all_x) * w)
                    fy = int(min(all_y) * h)
                    fw = int((max(all_x) - min(all_x)) * w)
                    fh = int((max(all_y) - min(all_y)) * h)

                    return FacialKeypoints(
                        forehead_y=forehead_y,
                        nose_y=nose_y,
                        chin_y=chin_y,
                        center_y=center_y,
                        bbox=(fx, fy, fw, fh),
                    )
            except Exception as exc:
                logger.debug("MediaPipe inference error: %s. Falling back to OpenCV.", exc)

        # 2. High-speed OpenCV Cascade Fallback (Optimized for ARM Cortex-A72)
        if self._cv_cascade is not None and not self._cv_cascade.empty():
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            # scaleFactor=1.2 and minNeighbors=3 runs 3x faster than 1.1 on ARM
            faces = self._cv_cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=3, minSize=(35, 35)
            )

            if len(faces) == 0:
                return None

            # Pick largest detected face
            best_face = max(faces, key=lambda r: int(r[2] * r[3]))
            fx, fy, fw, fh = (int(v) for v in best_face)
            frame_h = float(rgb_frame.shape[0])

            forehead_y = float(fy) / frame_h
            chin_y = float(fy + fh) / frame_h
            center_y = (float(fy) + (fh / 2.0)) / frame_h
            nose_y = (float(fy) + (0.52 * fh)) / frame_h

            return FacialKeypoints(
                forehead_y=forehead_y,
                nose_y=nose_y,
                chin_y=chin_y,
                center_y=center_y,
                bbox=(fx, fy, fw, fh),
            )

        return None

    def close(self) -> None:
        """Release underlying model resources."""
        if self._mp_mesh is not None:
            with contextlib.suppress(Exception):
                self._mp_mesh.close()
            self._mp_mesh = None
