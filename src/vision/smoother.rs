#[derive(Debug, Clone)]
pub struct EMASmoother {
    pub alpha: f32,
    pub deadzone: f32,
    pub max_alpha: f32,
    current_value: Option<f32>,
}

impl EMASmoother {
    pub fn new(alpha: f32, deadzone: f32, max_alpha: f32) -> Self {
        Self {
            alpha: alpha.clamp(0.01, 1.0),
            deadzone: deadzone.max(0.0),
            max_alpha: max_alpha.clamp(alpha, 1.0),
            current_value: None,
        }
    }

    pub fn filter(&mut self, target: f32) -> f32 {
        match self.current_value {
            None => {
                self.current_value = Some(target);
                target
            }
            Some(prev) => {
                let delta = (target - prev).abs();
                if delta < self.deadzone {
                    return prev;
                }

                // Dynamic speed adaptation: scale alpha up for fast intentional movements
                let velocity_factor = ((delta - self.deadzone) / 0.15).clamp(0.0, 1.0);
                let dynamic_alpha = self.alpha + (self.max_alpha - self.alpha) * velocity_factor;

                let smoothed = prev + (target - prev) * dynamic_alpha;
                self.current_value = Some(smoothed);
                smoothed
            }
        }
    }

    pub fn reset(&mut self) {
        self.current_value = None;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ema_initialization_and_deadzone() {
        let mut smoother = EMASmoother::new(0.3, 0.05, 0.7);
        // First value sets initial state
        assert_eq!(smoother.filter(0.5), 0.5);

        // Within deadzone (delta = 0.02 < 0.05), should return previous value
        assert_eq!(smoother.filter(0.52), 0.5);

        // Outside deadzone, should smooth towards target
        let next = smoother.filter(0.8);
        assert!(next > 0.5);
        assert!(next < 0.8);
    }
}
