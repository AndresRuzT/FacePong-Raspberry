"""Integration tests running headless simulated game loops."""

import os

# Configure headless SDL drivers before importing Pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "disk"

import pygame

from facepong.config.settings import AppConfig, GameConfig
from facepong.core.game import Game, GameState
from facepong.input.keyboard_input import KeyboardInputAdapter
from facepong.main import setup_adapters
from facepong.renderer.scenes.gameplay import GameplayRenderer
from facepong.renderer.scenes.menu import MenuRenderer
from facepong.renderer.screen import ScreenManager


def test_adapters_setup() -> None:
    """Verify input adapter setup with force keyboard flag."""
    config = AppConfig()
    a1, a2, t1, t2 = setup_adapters(config, force_keyboard=True)
    assert t1 == "keyboard"
    assert t2 == "keyboard"
    assert isinstance(a1, KeyboardInputAdapter)
    assert isinstance(a2, KeyboardInputAdapter)


def test_headless_gameplay_render() -> None:
    """Verify scene renderers draw to headless surfaces without errors."""
    config = AppConfig(game=GameConfig(winning_score=3))
    screen_mgr = ScreenManager(config.display)
    surface = screen_mgr.initialize()

    game = Game(config)
    menu_rend = MenuRenderer(config.display.width, config.display.height)
    game_rend = GameplayRenderer(config.display.width, config.display.height, config.debug)

    # Test Menu Rendering
    menu_rend.draw(surface)

    # Transition to Playing
    game.start_match()
    game_rend.draw(
        surface=surface,
        game=game,
        p1_detected=True,
        p2_detected=True,
        p1_type="keyboard",
        p2_type="keyboard",
        game_fps=60.0,
        cv_fps=20.0,
    )

    # Advance physics
    for _ in range(10):
        game.update(dt=0.016)

    # Test Pause Rendering
    game.toggle_pause()
    assert game.state == GameState.PAUSED
    game_rend.draw(
        surface=surface,
        game=game,
        p1_detected=True,
        p2_detected=True,
        p1_type="keyboard",
        p2_type="keyboard",
        game_fps=60.0,
        cv_fps=20.0,
    )

    # Trigger Game Over
    game.score.add_point(1)
    game.score.add_point(1)
    game.score.add_point(1)
    game.state = GameState.GAME_OVER
    game_rend.draw(
        surface=surface,
        game=game,
        p1_detected=False,
        p2_detected=False,
        p1_type="face",
        p2_type="face",
        game_fps=60.0,
        cv_fps=0.0,
    )

    pygame.quit()
