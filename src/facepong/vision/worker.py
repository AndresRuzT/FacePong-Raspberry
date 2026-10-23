"""Multiprocessing worker for non-blocking computer vision inference."""

from __future__ import annotations

import contextlib
import logging
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import cv2
import numpy as np

from facepong.vision.camera import CameraCapture
from facepong.vision.face_mesh import FaceMeshDetector
from facepong.vision.head_pose import HeadPoseEstimator

if TYPE_CHECKING:
    from facepong.config.settings import VisionConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VisionOutput:
    """Inter-process payload containing normalized player positions, status and preview frame."""

    p1_pos: float | None
    p1_detected: bool
    p2_pos: float | None
    p2_detected: bool
    fps: float
    timestamp: float
    preview_frame: bytes | None = None
    preview_size: tuple[int, int] = (240, 180)


def cv_worker_process(
    output_queue: mp.Queue[VisionOutput],
    stop_event: mp.synchronize.Event,
    config: VisionConfig,
    recalibrate_event: mp.synchronize.Event | None = None,
) -> None:
    """Worker function executed inside dedicated process on isolated CPU core.

    Args:
        output_queue: Queue carrying freshest detection results to main process.
        stop_event: Signal flag instructing the worker to gracefully exit.
        config: Vision configuration parameters.
        recalibrate_event: Optional event signaling recalibration of neutral baselines.
    """
    logger.info("Initializing CV worker process...")

    camera = CameraCapture(
        camera_index=config.camera_index,
        frame_width=config.frame_width,
        frame_height=config.frame_height,
        fps=config.fps,
    )

    if not camera.start():
        logger.error("CV Worker: Failed to start camera. Exiting worker process.")
        return

    # Dedicated face detectors for each half of the frame
    detector_p1 = FaceMeshDetector(
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
        model_complexity=config.model_complexity,
        refine_landmarks=config.refine_landmarks,
    )
    detector_p2 = FaceMeshDetector(
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
        model_complexity=config.model_complexity,
        refine_landmarks=config.refine_landmarks,
    )

    estimator_p1 = HeadPoseEstimator(
        neutral_ratio=config.neutral_ratio,
        sensitivity=config.sensitivity,
        smoothing_alpha=config.smoothing_alpha,
        deadzone=config.deadzone,
    )
    estimator_p2 = HeadPoseEstimator(
        neutral_ratio=config.neutral_ratio,
        sensitivity=config.sensitivity,
        smoothing_alpha=config.smoothing_alpha,
        deadzone=config.deadzone,
    )

    frame_count = 0
    start_time = time.monotonic()
    current_fps = 0.0
    preview_target_size = (240, 180)

    try:
        while not stop_event.is_set():
            # Check for recalibration request
            if recalibrate_event is not None and recalibrate_event.is_set():
                estimator_p1.calibrate()
                estimator_p2.calibrate()
                recalibrate_event.clear()
                logger.info("Recalibrated player neutral baselines.")

            p1_frame, p2_frame, full_frame = camera.read_split_frames()

            if p1_frame is None or p2_frame is None or full_frame is None:
                time.sleep(0.01)
                continue

            # Process Player 1 (Left side)
            kp1 = detector_p1.process_frame(p1_frame)
            p1_detected = kp1 is not None
            p1_pos = estimator_p1.estimate_vertical_position(kp1)

            # Process Player 2 (Right side)
            kp2 = detector_p2.process_frame(p2_frame)
            p2_detected = kp2 is not None
            p2_pos = estimator_p2.estimate_vertical_position(kp2)

            frame_count += 1
            now = time.monotonic()
            elapsed = now - start_time
            if elapsed >= 1.0:
                current_fps = frame_count / elapsed
                frame_count = 0
                start_time = now

            # Annotate full frame for live HUD preview
            annotated = full_frame.copy()
            h, w = annotated.shape[:2]
            mid = w // 2

            # Court dividing line
            cv2.line(annotated, (mid, 0), (mid, h), (100, 120, 140), 1)

            # Player 1 overlay (Cyan)
            if kp1 is not None:
                x1, y1, w1, h1 = kp1.bbox
                cv2.rectangle(annotated, (x1, y1), (x1 + w1, y1 + h1), (90, 200, 250), 2)
                cy1 = int(y1 + (h1 / 2))
                cv2.circle(annotated, (int(x1 + (w1 / 2)), cy1), 3, (90, 200, 250), -1)
                cv2.putText(
                    annotated,
                    "P1 OK",
                    (x1, max(14, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (90, 200, 250),
                    1,
                )
            else:
                cv2.putText(
                    annotated,
                    "P1 BUSCANDO",
                    (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (255, 69, 58),
                    1,
                )

            # Player 2 overlay (Amber / Orange)
            if kp2 is not None:
                x2, y2, w2, h2 = kp2.bbox
                # Offset by mid since kp2 is in the right subframe
                abs_x2 = mid + x2
                cv2.rectangle(annotated, (abs_x2, y2), (abs_x2 + w2, y2 + h2), (255, 149, 0), 2)
                cy2 = int(y2 + (h2 / 2))
                cv2.circle(annotated, (int(abs_x2 + (w2 / 2)), cy2), 3, (255, 149, 0), -1)
                cv2.putText(
                    annotated,
                    "P2 OK",
                    (abs_x2, max(14, y2 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 149, 0),
                    1,
                )
            else:
                cv2.putText(
                    annotated,
                    "P2 BUSCANDO",
                    (mid + 8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (255, 69, 58),
                    1,
                )

            # Resize annotated preview
            preview_resized = cv2.resize(
                annotated, preview_target_size, interpolation=cv2.INTER_NEAREST
            )
            preview_bytes = np.ascontiguousarray(preview_resized).tobytes()

            payload = VisionOutput(
                p1_pos=p1_pos,
                p1_detected=p1_detected,
                p2_pos=p2_pos,
                p2_detected=p2_detected,
                fps=current_fps,
                timestamp=now,
                preview_frame=preview_bytes,
                preview_size=preview_target_size,
            )

            # Freshest-frame delivery semantics
            if output_queue.full():
                with contextlib.suppress(Exception):
                    output_queue.get_nowait()

            with contextlib.suppress(Exception):
                output_queue.put_nowait(payload)

    finally:
        logger.info("Releasing CV worker resources...")
        camera.release()
        detector_p1.close()
        detector_p2.close()
