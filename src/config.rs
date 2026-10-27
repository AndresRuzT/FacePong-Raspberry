use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Deserialize)]
pub struct DisplayConfig {
    #[serde(default = "default_width")]
    pub width: i32,
    #[serde(default = "default_height")]
    pub height: i32,
    #[serde(default)]
    pub fullscreen: bool,
    #[serde(default = "default_fps")]
    pub fps_target: i32,
    #[serde(default = "default_title")]
    pub title: String,
}

fn default_width() -> i32 { 1280 }
fn default_height() -> i32 { 720 }
fn default_fps() -> i32 { 60 }
fn default_title() -> String { "FacePong — High Performance Rust HCI".to_string() }

impl Default for DisplayConfig {
    fn default() -> Self {
        Self {
            width: default_width(),
            height: default_height(),
            fullscreen: false,
            fps_target: default_fps(),
            title: default_title(),
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct GameConfig {
    #[serde(default = "default_winning_score")]
    pub winning_score: u32,
    #[serde(default = "default_paddle_width")]
    pub paddle_width: f32,
    #[serde(default = "default_paddle_height")]
    pub paddle_height: f32,
    #[serde(default = "default_paddle_speed")]
    pub paddle_speed: f32,
    #[serde(default = "default_paddle_margin_x")]
    pub paddle_margin_x: f32,
    #[serde(default = "default_ball_radius")]
    pub ball_radius: f32,
    #[serde(default = "default_ball_initial_speed")]
    pub ball_initial_speed: f32,
    #[serde(default = "default_ball_max_speed")]
    pub ball_max_speed: f32,
    #[serde(default = "default_speed_increment")]
    pub speed_increment: f32,
}

fn default_winning_score() -> u32 { 5 }
fn default_paddle_width() -> f32 { 18.0 }
fn default_paddle_height() -> f32 { 120.0 }
fn default_paddle_speed() -> f32 { 750.0 }
fn default_paddle_margin_x() -> f32 { 40.0 }
fn default_ball_radius() -> f32 { 10.0 }
fn default_ball_initial_speed() -> f32 { 420.0 }
fn default_ball_max_speed() -> f32 { 880.0 }
fn default_speed_increment() -> f32 { 1.06 }

impl Default for GameConfig {
    fn default() -> Self {
        Self {
            winning_score: default_winning_score(),
            paddle_width: default_paddle_width(),
            paddle_height: default_paddle_height(),
            paddle_speed: default_paddle_speed(),
            paddle_margin_x: default_paddle_margin_x(),
            ball_radius: default_ball_radius(),
            ball_initial_speed: default_ball_initial_speed(),
            ball_max_speed: default_ball_max_speed(),
            speed_increment: default_speed_increment(),
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct VisionConfig {
    #[serde(default)]
    pub camera_index: usize,
    #[serde(default = "default_frame_width")]
    pub frame_width: u32,
    #[serde(default = "default_frame_height")]
    pub frame_height: u32,
    #[serde(default = "default_cam_fps")]
    pub fps: u32,
    #[serde(default = "default_alpha")]
    pub smoothing_alpha: f32,
    #[serde(default = "default_sensitivity")]
    pub sensitivity: f32,
    #[serde(default = "default_upward_gain")]
    pub upward_gain: f32,
}

fn default_frame_width() -> u32 { 320 }
fn default_frame_height() -> u32 { 240 }
fn default_cam_fps() -> u32 { 30 }
fn default_alpha() -> f32 { 0.35 }
fn default_sensitivity() -> f32 { 5.5 }
fn default_upward_gain() -> f32 { 1.65 }

impl Default for VisionConfig {
    fn default() -> Self {
        Self {
            camera_index: 0,
            frame_width: default_frame_width(),
            frame_height: default_frame_height(),
            fps: 30,
            smoothing_alpha: default_alpha(),
            sensitivity: default_sensitivity(),
            upward_gain: default_upward_gain(),
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct ControlsConfig {
    #[serde(default = "default_face_control")]
    pub player1_input: String,
    #[serde(default = "default_face_control")]
    pub player2_input: String,
    #[serde(default)]
    pub invert_pitch: bool,
}

fn default_face_control() -> String { "face".to_string() }

impl Default for ControlsConfig {
    fn default() -> Self {
        Self {
            player1_input: default_face_control(),
            player2_input: default_face_control(),
            invert_pitch: false,
        }
    }
}

#[derive(Debug, Clone, Default, Deserialize)]
pub struct AppConfig {
    #[serde(default)]
    pub display: DisplayConfig,
    #[serde(default)]
    pub game: GameConfig,
    #[serde(default)]
    pub vision: VisionConfig,
    #[serde(default)]
    pub controls: ControlsConfig,
}

impl AppConfig {
    pub fn load_or_default<P: AsRef<Path>>(path: P) -> Self {
        if let Ok(content) = fs::read_to_string(&path) {
            match toml::from_str(&content) {
                Ok(cfg) => cfg,
                Err(err) => {
                    eprintln!("Warning: Failed to parse config file: {}. Using defaults.", err);
                    Self::default()
                }
            }
        } else {
            Self::default()
        }
    }
}
