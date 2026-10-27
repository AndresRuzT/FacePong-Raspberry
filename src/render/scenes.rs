use crate::core::game::{Game, GameState};
use crate::render::hud::{HUD, COLOR_P1, COLOR_P2, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY};
use macroquad::prelude::*;

pub const COLOR_BALL: Color = WHITE;
pub const COLOR_VICTORY: Color = Color::new(255.0 / 255.0, 215.0 / 255.0, 0.0, 1.0);

pub struct SceneRenderer;

impl SceneRenderer {
    pub fn draw_menu(
        screen_w: f32,
        screen_h: f32,
        preview_texture: Option<&Texture2D>,
    ) {
        clear_background(Color::new(10.0 / 255.0, 14.0 / 255.0, 22.0 / 255.0, 1.0));

        // Title
        let title = "FACE PONG";
        let title_m = measure_text(title, None, 64, 1.0);
        draw_text(
            title,
            (screen_w / 2.0) - (title_m.width / 2.0),
            72.0,
            64.0,
            COLOR_TEXT_PRIMARY,
        );

        // Subtitle
        let sub = "Sistema Interactivo HCI por Visión Artificial | Raspberry Pi 4";
        let sub_m = measure_text(sub, None, 18, 1.0);
        draw_text(
            sub,
            (screen_w / 2.0) - (sub_m.width / 2.0),
            104.0,
            18.0,
            COLOR_TEXT_MUTED,
        );

        // Camera Preview Alignment Box
        let cam_w = 320.0;
        let cam_h = 240.0;
        let cam_x = (screen_w / 2.0) - (cam_w / 2.0);
        let cam_y = 136.0;

        draw_rectangle(
            cam_x - 4.0,
            cam_y - 4.0,
            cam_w + 8.0,
            cam_h + 8.0,
            Color::new(18.0 / 255.0, 24.0 / 255.0, 34.0 / 255.0, 1.0),
        );
        draw_rectangle_lines(
            cam_x - 4.0,
            cam_y - 4.0,
            cam_w + 8.0,
            cam_h + 8.0,
            2.0,
            Color::new(55.0 / 255.0, 75.0 / 255.0, 105.0 / 255.0, 1.0),
        );

        if let Some(tex) = preview_texture {
            draw_texture_ex(
                tex,
                cam_x,
                cam_y,
                WHITE,
                DrawTextureParams {
                    dest_size: Some(vec2(cam_w, cam_h)),
                    ..Default::default()
                },
            );

            // Alignment Indicators
            draw_text("<< JUGADOR 1 (Izq)", cam_x + 8.0, cam_y + 22.0, 15.0, COLOR_P1);
            let p2_lbl = "JUGADOR 2 (Der) >>";
            let p2_m = measure_text(p2_lbl, None, 15, 1.0);
            draw_text(p2_lbl, cam_x + cam_w - p2_m.width - 8.0, cam_y + 22.0, 15.0, COLOR_P2);
        } else {
            let load_str = "INICIALIZANDO SENSOR DE VISIÓN...";
            let m = measure_text(load_str, None, 16, 1.0);
            draw_text(
                load_str,
                cam_x + (cam_w / 2.0) - (m.width / 2.0),
                cam_y + (cam_h / 2.0),
                16.0,
                COLOR_P1,
            );
        }

        // Action Prompts
        let prompt = "PRESIONA [ESPACIO] PARA INICIAR PARTIDA";
        let prompt_m = measure_text(prompt, None, 24, 1.0);
        draw_text(
            prompt,
            (screen_w / 2.0) - (prompt_m.width / 2.0),
            cam_y + cam_h + 46.0,
            24.0,
            COLOR_P1,
        );

        let hint1 = "Ubíquense frente a la cámara: P1 a la izquierda, P2 a la derecha.";
        let hint1_m = measure_text(hint1, None, 15, 1.0);
        draw_text(
            hint1,
            (screen_w / 2.0) - (hint1_m.width / 2.0),
            cam_y + cam_h + 74.0,
            15.0,
            COLOR_TEXT_MUTED,
        );

        let hint2 = "Inclina la cabeza arriba y abajo para controlar tu paleta en tiempo real.";
        let hint2_m = measure_text(hint2, None, 15, 1.0);
        draw_text(
            hint2,
            (screen_w / 2.0) - (hint2_m.width / 2.0),
            cam_y + cam_h + 96.0,
            15.0,
            COLOR_TEXT_MUTED,
        );

        HUD::draw_footer_help(screen_w, screen_h);
    }

    pub fn draw_gameplay(
        screen_w: f32,
        screen_h: f32,
        game: &Game,
        p1_detected: bool,
        p2_detected: bool,
        p1_type: &str,
        p2_type: &str,
        game_fps: f32,
        cv_fps: f32,
        preview_texture: Option<&Texture2D>,
    ) {
        clear_background(Color::new(10.0 / 255.0, 14.0 / 255.0, 22.0 / 255.0, 1.0));

        // 1. Top exterior dashboard frame
        HUD::draw_top_dashboard(
            screen_w,
            screen_h,
            p1_detected,
            p2_detected,
            p1_type,
            p2_type,
            game_fps,
            cv_fps,
            preview_texture,
        );

        // 2. Framed court arena (unobstructed field of play)
        HUD::draw_court(
            game.arena_x,
            game.arena_y,
            game.arena_w,
            game.arena_h,
            game.score.p1_score,
            game.score.p2_score,
        );

        // 3. Paddle 1 (Left - Cyan)
        draw_rectangle(
            game.paddle1.x,
            game.paddle1.y,
            game.paddle1.width,
            game.paddle1.height,
            COLOR_P1,
        );

        // 4. Paddle 2 (Right - Amber)
        draw_rectangle(
            game.paddle2.x,
            game.paddle2.y,
            game.paddle2.width,
            game.paddle2.height,
            COLOR_P2,
        );

        // 5. Ball
        draw_circle(game.ball.x, game.ball.y, game.ball.radius, COLOR_BALL);

        // 6. Overlays for Paused and GameOver states
        if game.state == GameState::Paused {
            draw_rectangle(
                game.arena_x,
                game.arena_y,
                game.arena_w,
                game.arena_h,
                Color::new(0.0, 0.0, 0.0, 0.70),
            );
            let pause_str = "JUEGO PAUSADO";
            let m = measure_text(pause_str, None, 48, 1.0);
            draw_text(
                pause_str,
                game.arena_x + (game.arena_w / 2.0) - (m.width / 2.0),
                game.arena_y + (game.arena_h / 2.0) - 10.0,
                48.0,
                WHITE,
            );
            let sub_pause = "Presiona [ESPACIO] para reanudar";
            let sm = measure_text(sub_pause, None, 20, 1.0);
            draw_text(
                sub_pause,
                game.arena_x + (game.arena_w / 2.0) - (sm.width / 2.0),
                game.arena_y + (game.arena_h / 2.0) + 30.0,
                20.0,
                COLOR_TEXT_MUTED,
            );
        } else if game.state == GameState::GameOver {
            draw_rectangle(
                game.arena_x,
                game.arena_y,
                game.arena_w,
                game.arena_h,
                Color::new(0.0, 0.0, 0.0, 0.80),
            );
            let winner_num = game.score.winner.unwrap_or(1);
            let win_str = format!("¡JUGADOR {} GANA LA PARTIDA!", winner_num);
            let m = measure_text(&win_str, None, 44, 1.0);
            draw_text(
                &win_str,
                game.arena_x + (game.arena_w / 2.0) - (m.width / 2.0),
                game.arena_y + (game.arena_h / 2.0) - 20.0,
                44.0,
                COLOR_VICTORY,
            );
            let sub_win = "Presiona [ESPACIO] o [R] para jugar otra vez";
            let sm = measure_text(sub_win, None, 20, 1.0);
            draw_text(
                sub_win,
                game.arena_x + (game.arena_w / 2.0) - (sm.width / 2.0),
                game.arena_y + (game.arena_h / 2.0) + 26.0,
                20.0,
                WHITE,
            );
        }

        HUD::draw_footer_help(screen_w, screen_h);
    }
}
