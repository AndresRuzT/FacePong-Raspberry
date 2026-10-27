use crate::config::AppConfig;
use crate::core::ball::Ball;
use crate::core::paddle::Paddle;
use crate::core::score::ScoreManager;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GameState {
    Menu,
    Playing,
    Paused,
    GameOver,
}

#[derive(Debug, Clone)]
pub struct Game {
    pub state: GameState,
    pub arena_x: f32,
    pub arena_y: f32,
    pub arena_w: f32,
    pub arena_h: f32,
    pub paddle1: Paddle,
    pub paddle2: Paddle,
    pub ball: Ball,
    pub score: ScoreManager,
}

impl Game {
    pub fn new(config: &AppConfig) -> Self {
        let arena_x = 24.0;
        let arena_y = 148.0;
        let arena_w = (config.display.width as f32) - 48.0;
        let arena_h = (config.display.height as f32) - 176.0;

        let pad_w = config.game.paddle_width;
        let pad_h = config.game.paddle_height;
        let pad_margin = config.game.paddle_margin_x;
        let pad_speed = config.game.paddle_speed;

        let paddle1 = Paddle::new(
            arena_x + pad_margin,
            arena_y + ((arena_h - pad_h) / 2.0),
            pad_w,
            pad_h,
            arena_h,
            pad_speed,
            arena_y,
        );

        let paddle2 = Paddle::new(
            arena_x + arena_w - pad_margin - pad_w,
            arena_y + ((arena_h - pad_h) / 2.0),
            pad_w,
            pad_h,
            arena_h,
            pad_speed,
            arena_y,
        );

        let ball = Ball::new(
            arena_w,
            arena_h,
            config.game.ball_radius,
            config.game.ball_initial_speed,
            config.game.ball_max_speed,
            config.game.speed_increment,
            arena_x,
            arena_y,
        );

        let score = ScoreManager::new(config.game.winning_score);

        Self {
            state: GameState::Menu,
            arena_x,
            arena_y,
            arena_w,
            arena_h,
            paddle1,
            paddle2,
            ball,
            score,
        }
    }

    pub fn start_match(&mut self) {
        self.state = GameState::Playing;
        self.score.reset();
        self.paddle1.reset();
        self.paddle2.reset();
        self.ball.reset(1);
    }

    pub fn toggle_pause(&mut self) {
        match self.state {
            GameState::Playing => self.state = GameState::Paused,
            GameState::Paused => self.state = GameState::Playing,
            _ => {}
        }
    }

    pub fn reset_match(&mut self) {
        self.score.reset();
        self.paddle1.reset();
        self.paddle2.reset();
        self.ball.reset(1);
        self.state = GameState::Playing;
    }

    pub fn update(&mut self, dt: f32) {
        if self.state != GameState::Playing {
            return;
        }

        self.paddle1.update(dt);
        self.paddle2.update(dt);

        if let Some(scoring_player) = self.ball.update(dt) {
            let is_over = self.score.add_point(scoring_player);
            if is_over {
                self.state = GameState::GameOver;
            } else {
                let launch_dir = if scoring_player == 1 { 1 } else { -1 };
                self.ball.reset(launch_dir);
            }
            return;
        }

        self.ball.check_paddle_collision(&self.paddle1);
        self.ball.check_paddle_collision(&self.paddle2);
    }
}
