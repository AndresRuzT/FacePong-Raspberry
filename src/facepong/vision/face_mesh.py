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
        self._eye_cascade: cv2.CascadeClassifier | None = None

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
            eye_xml = haarcascades_dir + "haarcascade_eye.xml"
            self._cv_cascade = cv2.CascadeClassifier(face_xml)
            self._eye_cascade = cv2.CascadeClassifier(eye_xml)
        except Exception as exc:
            logger.warning("Failed to initialize OpenCV Haar cascades: %s", exc)

    @property
    def is_available(self) -> bool:
        """Return True if any detection backend is operational."""
        return self._mp_mesh is not None or (
            self._cv_cascade is not None and not self._cv_cascade.empty()
        )

    def process_frame(self, rgb_frame: np.ndarray[Any, Any]) -> FacialKeypoints | None:
        """Process RGB frame and extract essential vertical keypoints.

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
                    return FacialKeypoints(
                        forehead_y=float(lm[LANDMARK_FOREHEAD].y),
                        nose_y=float(lm[LANDMARK_NOSE].y),
                        chin_y=float(lm[LANDMARK_CHIN].y),
                    )
            except Exception as exc:
                logger.debug("MediaPipe inference error: %s. Falling back to OpenCV.", exc)

        # 2. High-speed OpenCV Cascade Fallback (Optimized for ARM Cortex-A72)
        if self._cv_cascade is not None and not self._cv_cascade.empty():
            gray = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2GRAY)
            faces = self._cv_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
            )

            if len(faces) == 0:
                return None

            # Pick largest detected face
            best_face = max(faces, key=lambda r: int(r[2] * r[3]))
            fx, fy, fw, fh = (int(v) for v in best_face)
            frame_h = float(rgb_frame.shape[0])

            forehead_y = float(fy) / frame_h
            chin_y = float(fy + fh) / frame_h

            # Look for eyes within upper half of face to estimate gaze/pitch
            nose_y = float(fy + (0.50 * fh)) / frame_h
            if self._eye_cascade is not None and not self._eye_cascade.empty():
                face_upper = gray[fy : fy + int(fh * 0.6), fx : fx + fw]
                eyes = self._eye_cascade.detectMultiScale(
                    face_upper, scaleFactor=1.1, minNeighbors=3, minSize=(12, 12)
                )
                if len(eyes) > 0:
                    avg_eye_y = float(np.mean([ey + (eh / 2.0) for (_, ey, _, eh) in eyes]))
                    # Nose is located below eye midpoint
                    nose_y = (float(fy) + avg_eye_y + (0.22 * fh)) / frame_h

            return FacialKeypoints(
                forehead_y=forehead_y,
                nose_y=nose_y,
                chin_y=chin_y,
            )

        return None

    def close(self) -> None:
        """Release underlying model resources."""
        if self._mp_mesh is not None:
            with contextlib.suppress(Exception):
                self._mp_mesh.close()
            self._mp_mesh = None
