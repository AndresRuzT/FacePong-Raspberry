"""Multiprocessing worker for non-blocking computer vision inference."""

from __future__ import annotations

import contextlib
import logging
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from facepong.vision.camera import CameraCapture
from facepong.vision.face_mesh import FaceMeshDetector
from facepong.vision.head_pose import HeadPoseEstimator

if TYPE_CHECKING:
    from facepong.config.settings import VisionConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VisionOutput:
    """Inter-process payload containing normalized player positions and status."""

    p1_pos: float | None
    p1_detected: bool
    p2_pos: float | None
    p2_detected: bool
    fps: float
    timestamp: float


def cv_worker_process(
    output_queue: mp.Queue[VisionOutput],
    stop_event: mp.synchronize.Event,
    config: VisionConfig,
) -> None:
    """Worker function executed inside dedicated process on isolated CPU core.

    Args:
        output_queue: Queue carrying freshest detection results to main process.
        stop_event: Signal flag instructing the worker to gracefully exit.
        config: Vision configuration parameters.
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

    # Dedicated face mesh detectors for each half of the frame
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

    try:
        while not stop_event.is_set():
            p1_frame, p2_frame = camera.read_split_frames()

            if p1_frame is None or p2_frame is None:
                time.sleep(0.01)
                continue

            # Process Player 1
            kp1 = detector_p1.process_frame(p1_frame)
            p1_detected = kp1 is not None
            p1_pos = estimator_p1.estimate_vertical_position(kp1)

            # Process Player 2
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

            payload = VisionOutput(
                p1_pos=p1_pos,
                p1_detected=p1_detected,
                p2_pos=p2_pos,
                p2_detected=p2_detected,
                fps=current_fps,
                timestamp=now,
            )

            # Freshest-frame delivery semantics: drop previous frame if full
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
