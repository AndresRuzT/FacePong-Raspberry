"""Tests for high-level Game coordinator and state transitions."""

from facepong.config.settings import AppConfig, GameConfig
from facepong.core.game import Game, GameState


def test_game_initial_state() -> None:
    """Verify initial state is MENU."""
    game = Game(AppConfig())
    assert game.state == GameState.MENU
    assert game.score.p1_score == 0
    assert game.score.p2_score == 0


def test_game_start_and_pause() -> None:
    """Verify state transitions between MENU, PLAYING and PAUSED."""
    game = Game(AppConfig())
    game.start_match()
    assert game.state == GameState.PLAYING

    game.toggle_pause()
    assert game.state == GameState.PAUSED

    game.toggle_pause()
    assert game.state == GameState.PLAYING


def test_game_scoring_and_win() -> None:
    """Simulate scoring loop until GAME_OVER is achieved."""
    config = AppConfig(game=GameConfig(winning_score=2))
    game = Game(config)
    game.start_match()

    # Move ball past right wall to trigger point for Player 1
    game.ball.x = 2000.0
    game.ball.vx = 500.0
    game.update(dt=0.01)

    assert game.score.p1_score == 1
    assert game.state == GameState.PLAYING

    # Second point
    game.ball.x = 2000.0
    game.ball.vx = 500.0
    game.update(dt=0.01)

    assert game.score.p1_score == 2
    assert game.state == GameState.GAME_OVER
