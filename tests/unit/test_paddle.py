"""Tests for Paddle kinematics and clamping."""

from facepong.core.paddle import Paddle


def test_paddle_initialization() -> None:
    """Check initial position and bounds calculation."""
    paddle = Paddle(x=50.0, initial_y=300.0, width=20.0, height=100.0, bounds_height=720.0)
    assert paddle.x == 50.0
    assert paddle.y == 300.0
    assert paddle.width == 20.0
    assert paddle.height == 100.0
    assert paddle.min_y == 0.0
    assert paddle.max_y == 620.0
    assert paddle.center_y == 350.0


def test_paddle_clamping() -> None:
    """Ensure paddle cannot move past top or bottom arena boundaries."""
    paddle = Paddle(x=50.0, initial_y=1000.0, width=20.0, height=100.0, bounds_height=720.0)
    assert paddle.y == 620.0

    paddle.move_by_delta(-1000.0)
    assert paddle.y == 0.0


def test_paddle_normalized_targeting() -> None:
    """Test normalized positioning mapping [0.0, 1.0]."""
    paddle = Paddle(
        x=50.0, initial_y=0.0, width=20.0, height=100.0, bounds_height=720.0, speed=1000.0
    )

    # Move target to center (0.5)
    paddle.set_normalized_position(0.5)
    assert paddle.target_y == 310.0

    # Simulate 0.5s update: 1000 px/s * 0.5s = 500px, which reaches target 310
    paddle.update(0.5)
    assert paddle.y == 310.0


def test_paddle_reset() -> None:
    """Verify reset places paddle in center of arena."""
    paddle = Paddle(x=50.0, initial_y=0.0, width=20.0, height=100.0, bounds_height=720.0)
    paddle.reset()
    assert paddle.y == 310.0
