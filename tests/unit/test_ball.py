"""Tests for Ball kinematics and collision physics."""

from facepong.core.ball import Ball
from facepong.core.paddle import Paddle


def test_ball_initialization() -> None:
    """Verify default initial position is center arena."""
    ball = Ball(bounds_width=1280.0, bounds_height=720.0, radius=10.0, initial_speed=400.0)
    assert ball.x == 640.0
    assert ball.y == 360.0
    assert ball.current_speed == 400.0


def test_ball_wall_bounce() -> None:
    """Ensure ball reflects vertical velocity upon hitting top/bottom boundaries."""
    ball = Ball(bounds_width=1280.0, bounds_height=720.0, radius=10.0, initial_speed=400.0)
    # Force position close to top boundary and moving up
    ball.y = 5.0
    ball.vy = -300.0
    score_event = ball.update(dt=0.1)

    assert score_event is None
    assert ball.vy > 0.0  # Reflected downwards
    assert ball.y >= ball.radius


def test_ball_score_event() -> None:
    """Ball crossing left/right boundaries must return scoring player."""
    ball = Ball(bounds_width=1280.0, bounds_height=720.0, radius=10.0, initial_speed=500.0)

    # Ball moves left past x=0
    ball.x = -15.0
    ball.vx = -100.0
    score_event = ball.update(dt=0.01)
    assert score_event == 2  # Player 2 scores

    # Ball moves right past x=bounds_width
    ball.x = 1300.0
    ball.vx = 100.0
    score_event = ball.update(dt=0.01)
    assert score_event == 1  # Player 1 scores


def test_paddle_collision() -> None:
    """Ball striking paddle rebounds and increases speed."""
    ball = Ball(bounds_width=1280.0, bounds_height=720.0, radius=10.0, initial_speed=400.0)
    paddle = Paddle(x=40.0, initial_y=300.0, width=20.0, height=120.0, bounds_height=720.0)

    # Position ball moving towards left paddle
    ball.x = 65.0
    ball.y = 360.0
    ball.vx = -400.0
    ball.vy = 0.0

    hit = ball.check_paddle_collision(paddle)
    assert hit is True
    assert ball.vx > 0.0  # Deflected to the right
    assert ball.current_speed > 400.0  # Speed progressively accelerated
