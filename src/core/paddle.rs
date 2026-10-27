#[derive(Debug, Clone)]
pub struct Paddle {
    pub x: f32,
    pub y: f32,
    pub width: f32,
    pub height: f32,
    pub bounds_top: f32,
    pub bounds_height: f32,
    pub speed: f32,
    pub min_y: f32,
    pub max_y: f32,
    pub target_y: Option<f32>,
}

impl Paddle {
    pub fn new(
        x: f32,
        initial_y: f32,
        width: f32,
        height: f32,
        bounds_height: f32,
        speed: f32,
        bounds_top: f32,
    ) -> Self {
        let min_y = bounds_top;
        let max_y = (bounds_top + bounds_height - height).max(min_y);
        let mut paddle = Self {
            x,
            y: initial_y,
            width,
            height,
            bounds_top,
            bounds_height,
            speed,
            min_y,
            max_y,
            target_y: None,
        };
        paddle.y = paddle.clamp(initial_y);
        paddle
    }

    #[inline]
    pub fn clamp(&self, val: f32) -> f32 {
        val.clamp(self.min_y, self.max_y)
    }

    #[inline]
    pub fn center_y(&self) -> f32 {
        self.y + (self.height / 2.0)
    }

    pub fn set_normalized_position(&mut self, norm_y: f32) {
        let clamped_norm = norm_y.clamp(0.0, 1.0);
        self.target_y = Some(self.min_y + (clamped_norm * (self.max_y - self.min_y)));
    }

    pub fn move_by_delta(&mut self, dy: f32) {
        self.y = self.clamp(self.y + dy);
        self.target_y = None;
    }

    pub fn update(&mut self, dt: f32) {
        if let Some(target) = self.target_y {
            let diff = target - self.y;
            if diff.abs() < 0.5 {
                self.y = target;
                return;
            }
            // Continuous organic 60 FPS lerp: smooth gliding without jumps or lag
            let lerp_step = diff * (26.0 * dt).min(1.0);
            self.y = self.clamp(self.y + lerp_step);
        }
    }

    pub fn reset(&mut self) {
        self.y = self.clamp(self.bounds_top + ((self.bounds_height - self.height) / 2.0));
        self.target_y = None;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_paddle_clamping() {
        let paddle = Paddle::new(10.0, 100.0, 15.0, 100.0, 500.0, 600.0, 50.0);
        assert_eq!(paddle.min_y, 50.0);
        assert_eq!(paddle.max_y, 450.0);
        assert_eq!(paddle.clamp(10.0), 50.0);
        assert_eq!(paddle.clamp(500.0), 450.0);
    }

    #[test]
    fn test_paddle_normalized_position() {
        let mut paddle = Paddle::new(10.0, 100.0, 15.0, 100.0, 500.0, 600.0, 0.0);
        paddle.set_normalized_position(0.0);
        assert_eq!(paddle.target_y, Some(0.0));
        paddle.set_normalized_position(1.0);
        assert_eq!(paddle.target_y, Some(400.0));
    }

    #[test]
    fn test_paddle_lerp_glide() {
        let mut paddle = Paddle::new(10.0, 200.0, 15.0, 100.0, 500.0, 600.0, 0.0);
        paddle.set_normalized_position(1.0); // target 400.0
        paddle.update(0.016); // 1 frame at 60fps
        assert!(paddle.y > 200.0);
        assert!(paddle.y < 400.0);
    }
}
