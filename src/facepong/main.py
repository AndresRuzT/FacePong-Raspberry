"""Main entry point and execution loop for FacePong."""

from __future__ import annotations

import argparse
import contextlib
import logging
import multiprocessing as mp
import sys

import pygame

from facepong.config.loader import load_config
from facepong.config.settings import AppConfig
from facepong.core.game import Game, GameState
from facepong.input.base import InputAdapter
from facepong.input.face_input import FaceInputAdapter
from facepong.input.keyboard_input import KeyboardInputAdapter
from facepong.renderer.scenes.gameplay import GameplayRenderer
from facepong.renderer.scenes.menu import MenuRenderer
from facepong.renderer.screen import ScreenManager
from facepong.vision.worker import VisionOutput, cv_worker_process

logger = logging.getLogger("facepong")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="facepong",
        description="FacePong: Real-time computer vision Pong on Raspberry Pi 4",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/default.toml",
        help="Path to custom TOML configuration file",
    )
    parser.add_argument(
        "--keyboard",
        action="store_true",
        help="Force keyboard controls for both players (fallback mode)",
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Launch display in fullscreen mode",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Override camera hardware device index (e.g. 0)",
    )
    return parser.parse_args()


def setup_adapters(
    config: AppConfig, force_keyboard: bool
) -> tuple[InputAdapter, InputAdapter, str, str]:
    """Configure input adapters based on configuration and flags."""
    p1_type = "keyboard" if force_keyboard else config.controls.player1_input
    p2_type = "keyboard" if force_keyboard else config.controls.player2_input

    # Player 1 Adapter
    if p1_type == "keyboard":
        adapter_p1: InputAdapter = KeyboardInputAdapter(
            key_up=pygame.K_w,
            key_down=pygame.K_s,
            speed=config.game.paddle_speed,
        )
    else:
        adapter_p1 = FaceInputAdapter(player_id=1)

    # Player 2 Adapter
    if p2_type == "keyboard":
        adapter_p2: InputAdapter = KeyboardInputAdapter(
            key_up=pygame.K_UP,
            key_down=pygame.K_DOWN,
            speed=config.game.paddle_speed,
        )
    else:
        adapter_p2 = FaceInputAdapter(player_id=2)

    return adapter_p1, adapter_p2, p1_type, p2_type


def main() -> int:
    """Application entry point."""
    args = parse_arguments()
    config = load_config(args.config)

    # Logging setup
    log_level = getattr(logging, config.debug.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting FacePong version 0.1.0...")

    # Screen setup
    screen_mgr = ScreenManager(config.display)
    surface = screen_mgr.initialize()

    # Core game instance
    game = Game(config)
    adapter_p1, adapter_p2, p1_type, p2_type = setup_adapters(config, args.keyboard)

    # Start CV worker process if any player is using face control
    vision_process: mp.Process | None = None
    stop_event = mp.Event()
    recalibrate_event = mp.Event()
    vision_queue: mp.Queue[VisionOutput] = mp.Queue(maxsize=1)

    needs_cv = (p1_type == "face") or (p2_type == "face")
    if needs_cv:
        logger.info("Starting computer vision background worker process...")
        vision_process = mp.Process(
            target=cv_worker_process,
            args=(vision_queue, stop_event, config.vision, recalibrate_event),
            daemon=True,
        )
        vision_process.start()

    # Scene renderers
    menu_renderer = MenuRenderer(config.display.width, config.display.height)
    gameplay_renderer = GameplayRenderer(config.display.width, config.display.height, config.debug)

    clock = pygame.time.Clock()
    running = True
    cv_fps = 0.0
    show_preview = config.debug.show_camera_preview
    current_preview_surface: pygame.Surface | None = None

    try:
        while running:
            dt = clock.tick_busy_loop(config.display.fps_target) / 1000.0

            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break

                    if event.key == pygame.K_SPACE:
                        if game.state == GameState.MENU:
                            recalibrate_event.set()
                            game.start_match()
                        elif game.state in (GameState.PLAYING, GameState.PAUSED):
                            game.toggle_pause()
                        elif game.state == GameState.GAME_OVER:
                            recalibrate_event.set()
                            game.start_match()

                    elif event.key == pygame.K_c:
                        # Instant recalibration of resting neutral position
                        recalibrate_event.set()
                        logger.info("Player recalibration triggered via key [C].")

                    elif event.key == pygame.K_v:
                        # Toggle camera PiP preview visibility
                        show_preview = not show_preview

                    elif event.key == pygame.K_r:
                        recalibrate_event.set()
                        game.reset_match()

                # Dispatch keyboard strokes to adapters if active
                if isinstance(adapter_p1, KeyboardInputAdapter):
                    adapter_p1.handle_event(event)
                if isinstance(adapter_p2, KeyboardInputAdapter):
                    adapter_p2.handle_event(event)

            if not running:
                break

            # 2. Ingest Latest CV Data (Non-blocking)
            if needs_cv:
                latest_cv: VisionOutput | None = None
                while not vision_queue.empty():
                    with contextlib.suppress(Exception):
                        latest_cv = vision_queue.get_nowait()

                if latest_cv is not None:
                    cv_fps = latest_cv.fps
                    if isinstance(adapter_p1, FaceInputAdapter):
                        adapter_p1.update_from_vision(latest_cv.p1_pos, latest_cv.p1_detected)
                    if isinstance(adapter_p2, FaceInputAdapter):
                        adapter_p2.update_from_vision(latest_cv.p2_pos, latest_cv.p2_detected)

                    if latest_cv.preview_frame is not None:
                        current_preview_surface = pygame.image.frombuffer(
                            latest_cv.preview_frame, latest_cv.preview_size, "RGB"
                        )

            # 3. Update Paddle Kinematics from Input Adapters
            p1_norm = adapter_p1.get_normalized_position()
            if p1_norm is not None:
                game.paddle1.set_normalized_position(p1_norm)
            else:
                game.paddle1.move_by_delta(adapter_p1.get_delta_y(dt))

            p2_norm = adapter_p2.get_normalized_position()
            if p2_norm is not None:
                game.paddle2.set_normalized_position(p2_norm)
            else:
                game.paddle2.move_by_delta(adapter_p2.get_delta_y(dt))

            # 4. Advance Game Physics
            game.update(dt)

            # 5. Render Scene
            screen_mgr.clear()

            if game.state == GameState.MENU:
                menu_renderer.draw(surface, preview_surface=current_preview_surface)
            else:
                gameplay_renderer.draw(
                    surface=surface,
                    game=game,
                    p1_detected=adapter_p1.is_detected(),
                    p2_detected=adapter_p2.is_detected(),
                    p1_type=p1_type,
                    p2_type=p2_type,
                    game_fps=clock.get_fps(),
                    cv_fps=cv_fps,
                    preview_surface=current_preview_surface,
                    show_preview=show_preview,
                )

            screen_mgr.flip()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Exiting FacePong...")
    finally:
        logger.info("Shutting down FacePong gracefully...")
        if vision_process is not None:
            stop_event.set()
            vision_process.join(timeout=1.5)
            if vision_process.is_alive():
                vision_process.terminate()

        pygame.quit()

    return 0


if __name__ == "__main__":
    # Use forkserver start method for safe C-extension multiprocessing
    with contextlib.suppress(RuntimeError, ValueError):
        mp.set_start_method("forkserver")

    sys.exit(main())
