pub mod config;
pub mod core;
pub mod render;
pub mod vision;

use crate::config::AppConfig;
use crate::core::game::{Game, GameState};
use crate::render::SceneRenderer;
use crate::vision::{CameraSystem, VisionFrame};
use macroquad::prelude::*;
use std::path::Path;

fn window_conf() -> Conf {
    Conf {
        window_title: "FacePong — High Performance Rust HCI".to_string(),
        window_width: 1280,
        window_height: 720,
        fullscreen: false,
        window_resizable: false,
        ..Default::default()
    }
}

#[macroquad::main(window_conf)]
async fn main() {
    let config_path = Path::new("config/config.toml");
    let config = AppConfig::load_or_default(config_path);

    let mut game = Game::new(&config);
    let camera_system = CameraSystem::start(config.vision.clone());

    let mut preview_texture: Option<Texture2D> = None;
    let mut last_vision_frame: Option<VisionFrame> = None;

    let mut frame_count = 0u32;
    let mut fps_timer = 0.0f32;
    let mut current_game_fps = 60.0f32;

    loop {
        let dt = get_frame_time().min(0.05);

        // Frame rate calculation
        frame_count += 1;
        fps_timer += dt;
        if fps_timer >= 0.5 {
            current_game_fps = (frame_count as f32) / fps_timer;
            frame_count = 0;
            fps_timer = 0.0;
        }

        // 1. Drain latest vision frame from background worker
        while let Ok(frame) = camera_system.receiver.try_recv() {
            if let Some(ref mut tex) = preview_texture {
                if tex.width() == frame.width as f32 && tex.height() == frame.height as f32 {
                    tex.update(&Image {
                        bytes: frame.rgba_data.clone(),
                        width: frame.width as u16,
                        height: frame.height as u16,
                    });
                } else {
                    let img = Image {
                        bytes: frame.rgba_data.clone(),
                        width: frame.width as u16,
                        height: frame.height as u16,
                    };
                    *tex = Texture2D::from_image(&img);
                }
            } else {
                let img = Image {
                    bytes: frame.rgba_data.clone(),
                    width: frame.width as u16,
                    height: frame.height as u16,
                };
                preview_texture = Some(Texture2D::from_image(&img));
            }
            last_vision_frame = Some(frame);
        }

        // 2. Global Hotkeys
        if is_key_pressed(KeyCode::Escape) {
            break;
        }

        if is_key_pressed(KeyCode::Space) {
            match game.state {
                GameState::Menu => game.start_match(),
                GameState::Playing | GameState::Paused => game.toggle_pause(),
                GameState::GameOver => game.reset_match(),
            }
        }

        if is_key_pressed(KeyCode::C) {
            camera_system.recalibrate();
        }

        if is_key_pressed(KeyCode::R) {
            game.reset_match();
        }

        // 3. Paddle Input Dispatch
        if let Some(ref frame) = last_vision_frame {
            if config.controls.player1_input == "face" && frame.p1_detected {
                game.paddle1.set_normalized_position(frame.p1_norm_y);
            }
            if config.controls.player2_input == "face" && frame.p2_detected {
                game.paddle2.set_normalized_position(frame.p2_norm_y);
            }
        }

        // Keyboard controls (either as primary input or instant override)
        let kb_step = config.game.paddle_speed * dt;
        if is_key_down(KeyCode::W) {
            game.paddle1.move_by_delta(-kb_step);
        }
        if is_key_down(KeyCode::S) {
            game.paddle1.move_by_delta(kb_step);
        }
        if is_key_down(KeyCode::Up) {
            game.paddle2.move_by_delta(-kb_step);
        }
        if is_key_down(KeyCode::Down) {
            game.paddle2.move_by_delta(kb_step);
        }

        // 4. Game Physics Update
        game.update(dt);

        // 5. Render Scene
        let screen_w = screen_width();
        let screen_h = screen_height();

        let (p1_det, p2_det, cv_fps) = match &last_vision_frame {
            Some(f) => (f.p1_detected, f.p2_detected, f.cv_fps),
            None => (false, false, 0.0),
        };

        if game.state == GameState::Menu {
            SceneRenderer::draw_menu(screen_w, screen_h, preview_texture.as_ref());
        } else {
            SceneRenderer::draw_gameplay(
                screen_w,
                screen_h,
                &game,
                p1_det,
                p2_det,
                &config.controls.player1_input,
                &config.controls.player2_input,
                current_game_fps,
                cv_fps,
                preview_texture.as_ref(),
            );
        }

        next_frame().await;
    }
}
