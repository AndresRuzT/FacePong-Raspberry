"""Ball physics and collision detection for FacePong."""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from facepong.core.paddle import Paddle


class Ball:
    """Represents the game ball with floating-point dynamics and paddle deflections."""

    def __init__(
        self,
        bounds_width: float,
        bounds_height: float,
        radius: float = 10.0,
        initial_speed: float = 420.0,
        max_speed: float = 880.0,
        speed_increment: float = 1.06,
    ) -> None:
        """Initialize ball physical properties and arena limits.

        Args:
            bounds_width: Arena width in pixels.
            bounds_height: Arena height in pixels.
            radius: Ball radius in pixels.
            initial_speed: Starting velocity in pixels per second.
            max_speed: Upper cap for ball velocity.
            speed_increment: Multiplier applied upon each paddle deflection.
        """
        self.bounds_width = float(bounds_width)
        self.bounds_height = float(bounds_height)
        self.radius = float(radius)
        self.initial_speed = float(initial_speed)
        self.max_speed = float(max_speed)
        self.speed_increment = float(speed_increment)

        self.x = self.bounds_width / 2.0
        self.y = self.bounds_height / 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.current_speed = self.initial_speed

        self.reset(direction=1)

    def reset(self, direction: int = 1) -> None:
        """Reset ball to screen center with a launch angle.

        Args:
            direction: 1 to launch towards the right (Player 2),
                      -1 to launch towards the left (Player 1).
        """
        self.x = self.bounds_width / 2.0
        self.y = self.bounds_height / 2.0
        self.current_speed = self.initial_speed

        # Launch angle between -35 and +35 degrees
        angle_rad = random.uniform(-math.radians(35), math.radians(35))
        dir_mult = 1.0 if direction >= 0 else -1.0

        self.vx = dir_mult * self.current_speed * math.cos(angle_rad)
        self.vy = self.current_speed * math.sin(angle_rad)

    def update(self, dt: float) -> int | None:
        """Advance ball position and handle upper/lower arena wall bounces.

        Args:
            dt: Delta time in seconds since previous frame.

        Returns:
            None if ball remains in play.
            1 if Player 1 scores (ball exited right boundary).
            2 if Player 2 scores (ball exited left boundary).
        """
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce against top wall
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)

        # Bounce against bottom wall
        elif self.y + self.radius >= self.bounds_height:
            self.y = self.bounds_height - self.radius
            self.vy = -abs(self.vy)

        # Check out-of-bounds score conditions
        if self.x + self.radius < 0:
            return 2  # Ball went past left edge -> Player 2 scores
        if self.x - self.radius > self.bounds_width:
            return 1  # Ball went past right edge -> Player 1 scores

        return None

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Detect and resolve collision between ball and paddle.

        Uses swept AABB / circle intersection and applies angular deflection
        based on the impact point along the paddle height.

        Args:
            paddle: The paddle instance to test against.

        Returns:
            True if collision occurred and was resolved, False otherwise.
        """
        # Find closest point on paddle rectangle to ball center
        px, py, pw, ph = paddle.rect
        closest_x = max(px, min(self.x, px + pw))
        closest_y = max(py, min(self.y, py + ph))

        dist_x = self.x - closest_x
        dist_y = self.y - closest_y
        distance_sq = (dist_x * dist_x) + (dist_y * dist_y)

        # Circle-to-box collision
        if distance_sq > (self.radius * self.radius):
            return False

        # Determine if paddle is left or right oriented
        is_left_paddle = px < (self.bounds_width / 2.0)

        # Ensure collision is only handled when moving towards the paddle
        if is_left_paddle and self.vx > 0:
            return False
        if not is_left_paddle and self.vx < 0:
            return False

        # Calculate normalized impact offset (-1.0 to +1.0)
        impact_offset = (self.y - paddle.center_y) / (paddle.height / 2.0)
        impact_offset = max(-1.0, min(impact_offset, 1.0))

        # Increase ball velocity progressively up to max_speed
        self.current_speed = min(self.current_speed * self.speed_increment, self.max_speed)

        # Calculate deflection angle (max 55 degrees)
        max_bounce_angle = math.radians(55)
        bounce_angle = impact_offset * max_bounce_angle

        if is_left_paddle:
            self.vx = self.current_speed * math.cos(bounce_angle)
            self.vy = self.current_speed * math.sin(bounce_angle)
            # Reposition outside paddle to prevent penetration
            self.x = px + pw + self.radius + 1.0
        else:
            self.vx = -self.current_speed * math.cos(bounce_angle)
            self.vy = self.current_speed * math.sin(bounce_angle)
            self.x = px - self.radius - 1.0

        return True
