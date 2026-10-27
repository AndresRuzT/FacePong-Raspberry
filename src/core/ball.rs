use crate::core::paddle::Paddle;
use std::f32::consts::PI;

#[derive(Debug, Clone)]
pub struct Ball {
    pub bounds_x: f32,
    pub bounds_y: f32,
    pub bounds_width: f32,
    pub bounds_height: f32,
    pub radius: f32,
    pub initial_speed: f32,
    pub max_speed: f32,
    pub speed_increment: f32,
    pub x: f32,
    pub y: f32,
    pub vx: f32,
    pub vy: f32,
    pub current_speed: f32,
    rng_state: u64,
}

impl Ball {
    pub fn new(
        bounds_width: f32,
        bounds_height: f32,
        radius: f32,
        initial_speed: f32,
        max_speed: f32,
        speed_increment: f32,
        bounds_x: f32,
        bounds_y: f32,
    ) -> Self {
        let mut ball = Self {
            bounds_x,
            bounds_y,
            bounds_width,
            bounds_height,
            radius,
            initial_speed,
            max_speed,
            speed_increment,
            x: bounds_x + (bounds_width / 2.0),
            y: bounds_y + (bounds_height / 2.0),
            vx: 0.0,
            vy: 0.0,
            current_speed: initial_speed,
            rng_state: 0x853c49e6748fea9b,
        };
        ball.reset(1);
        ball
    }

    #[inline]
    fn pseudo_random_f32(&mut self) -> f32 {
        // High-speed lightweight xorshift64* PRNG: deterministic and zero-dependency
        self.rng_state ^= self.rng_state >> 12;
        self.rng_state ^= self.rng_state << 25;
        self.rng_state ^= self.rng_state >> 27;
        let val = self.rng_state.wrapping_mul(0x2545F4914F6CDD1D);
        ((val >> 40) as f32) / 16777216.0 // normalized [0.0, 1.0)
    }

    pub fn reset(&mut self, direction: i32) {
        self.x = self.bounds_x + (self.bounds_width / 2.0);
        self.y = self.bounds_y + (self.bounds_height / 2.0);
        self.current_speed = self.initial_speed;

        // Launch angle between -35 and +35 degrees (±0.6108 rad)
        let r = self.pseudo_random_f32();
        let max_rad = 35.0 * (PI / 180.0);
        let angle_rad = (r * 2.0 - 1.0) * max_rad;
        let dir_mult = if direction >= 0 { 1.0 } else { -1.0 };

        self.vx = dir_mult * self.current_speed * angle_rad.cos();
        self.vy = self.current_speed * angle_rad.sin();
    }

    pub fn update(&mut self, dt: f32) -> Option<u32> {
        self.x += self.vx * dt;
        self.y += self.vy * dt;

        // Wall reflections (top / bottom boundaries)
        if self.y - self.radius <= self.bounds_y {
            self.y = self.bounds_y + self.radius;
            self.vy = self.vy.abs();
        } else if self.y + self.radius >= self.bounds_y + self.bounds_height {
            self.y = self.bounds_y + self.bounds_height - self.radius;
            self.vy = -self.vy.abs();
        }

        // Out-of-bounds score evaluation
        if self.x + self.radius < self.bounds_x {
            Some(2) // Past left edge -> Player 2 scores
        } else if self.x - self.radius > self.bounds_x + self.bounds_width {
            Some(1) // Past right edge -> Player 1 scores
        } else {
            None
        }
    }

    pub fn check_paddle_collision(&mut self, paddle: &Paddle) -> bool {
        let px = paddle.x;
        let py = paddle.y;
        let pw = paddle.width;
        let ph = paddle.height;

        let closest_x = self.x.clamp(px, px + pw);
        let closest_y = self.y.clamp(py, py + ph);

        let dist_x = self.x - closest_x;
        let dist_y = self.y - closest_y;
        let distance_sq = (dist_x * dist_x) + (dist_y * dist_y);

        if distance_sq > (self.radius * self.radius) {
            return false;
        }

        let arena_center_x = self.bounds_x + (self.bounds_width / 2.0);
        let is_left_paddle = px < arena_center_x;

        if is_left_paddle && self.vx > 0.0 {
            return false;
        }
        if !is_left_paddle && self.vx < 0.0 {
            return false;
        }

        // Normalized impact offset (-1.0 at paddle top to +1.0 at paddle bottom)
        let impact_offset = ((self.y - paddle.center_y()) / (ph / 2.0)).clamp(-1.0, 1.0);

        // Progressive acceleration up to max speed cap
        self.current_speed = (self.current_speed * self.speed_increment).min(self.max_speed);

        // Max deflection angle of 55 degrees
        let max_bounce_angle = 55.0 * (PI / 180.0);
        let bounce_angle = impact_offset * max_bounce_angle;

        if is_left_paddle {
            self.vx = self.current_speed * bounce_angle.cos();
            self.vy = self.current_speed * bounce_angle.sin();
            self.x = px + pw + self.radius + 1.0;
        } else {
            self.vx = -self.current_speed * bounce_angle.cos();
            self.vy = self.current_speed * bounce_angle.sin();
            self.x = px - self.radius - 1.0;
        }

        true
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ball_wall_bounces() {
        let mut ball = Ball::new(800.0, 600.0, 10.0, 300.0, 800.0, 1.05, 0.0, 0.0);
        ball.y = 8.0;
        ball.vy = -100.0;
        ball.update(0.01);
        assert!(ball.vy > 0.0); // bounced downward

        ball.y = 595.0;
        ball.vy = 100.0;
        ball.update(0.01);
        assert!(ball.vy < 0.0); // bounced upward
    }

    #[test]
    fn test_ball_scoring() {
        let mut ball = Ball::new(800.0, 600.0, 10.0, 300.0, 800.0, 1.05, 0.0, 0.0);
        ball.x = -15.0;
        let score = ball.update(0.01);
        assert_eq!(score, Some(2)); // P2 scores

        ball.x = 815.0;
        let score2 = ball.update(0.01);
        assert_eq!(score2, Some(1)); // P1 scores
    }

    #[test]
    fn test_ball_paddle_collision() {
        let mut ball = Ball::new(800.0, 600.0, 10.0, 300.0, 800.0, 1.10, 0.0, 0.0);
        let paddle = Paddle::new(20.0, 200.0, 20.0, 100.0, 600.0, 600.0, 0.0);
        ball.x = 35.0;
        ball.y = 250.0;
        ball.vx = -300.0;
        let hit = ball.check_paddle_collision(&paddle);
        assert!(hit);
        assert!(ball.vx > 0.0);
        assert!(ball.current_speed > 300.0);
    }
}
