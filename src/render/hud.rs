use macroquad::prelude::*;

pub const COLOR_BG_PANEL: Color = Color::new(20.0 / 255.0, 25.0 / 255.0, 36.0 / 255.0, 1.0);
pub const COLOR_BORDER_PANEL: Color = Color::new(42.0 / 255.0, 54.0 / 255.0, 76.0 / 255.0, 1.0);
pub const COLOR_COURT_BG: Color = Color::new(14.0 / 255.0, 18.0 / 255.0, 27.0 / 255.0, 1.0);
pub const COLOR_COURT_BORDER: Color = Color::new(55.0 / 255.0, 72.0 / 255.0, 100.0 / 255.0, 1.0);
pub const COLOR_NET: Color = Color::new(40.0 / 255.0, 52.0 / 255.0, 72.0 / 255.0, 1.0);

pub const COLOR_P1: Color = Color::new(0.0 / 255.0, 220.0 / 255.0, 255.0 / 255.0, 1.0);
pub const COLOR_P2: Color = Color::new(255.0 / 255.0, 150.0 / 255.0, 20.0 / 255.0, 1.0);
pub const COLOR_TEXT_PRIMARY: Color = Color::new(240.0 / 255.0, 245.0 / 255.0, 250.0 / 255.0, 1.0);
pub const COLOR_TEXT_MUTED: Color = Color::new(130.0 / 255.0, 145.0 / 255.0, 165.0 / 255.0, 1.0);
pub const COLOR_STATUS_ACTIVE: Color = Color::new(50.0 / 255.0, 215.0 / 255.0, 75.0 / 255.0, 1.0);
pub const COLOR_STATUS_INACTIVE: Color = Color::new(255.0 / 255.0, 69.0 / 255.0, 58.0 / 255.0, 1.0);

pub struct HUD;

impl HUD {
    pub fn draw_top_dashboard(
        screen_w: f32,
        _screen_h: f32,
        p1_detected: bool,
        p2_detected: bool,
        p1_type: &str,
        p2_type: &str,
        game_fps: f32,
        cv_fps: f32,
        preview_texture: Option<&Texture2D>,
    ) {
        // Upper exterior dashboard panel
        let panel_x = 18.0;
        let panel_y = 8.0;
        let panel_w = screen_w - 36.0;
        let panel_h = 130.0;

        draw_rectangle(panel_x, panel_y, panel_w, panel_h, COLOR_BG_PANEL);
        draw_rectangle_lines(panel_x, panel_y, panel_w, panel_h, 2.0, COLOR_BORDER_PANEL);

        // 1. Left Branding Block
        draw_text("FACEPONG", 36.0, 42.0, 32.0, COLOR_TEXT_PRIMARY);
        draw_text("HCI RESEARCH LAB | RPi 4", 36.0, 60.0, 16.0, COLOR_TEXT_MUTED);

        // Player 1 Badge
        let p1_card_x = 36.0;
        let p1_card_y = 72.0;
        let p1_card_w = 210.0;
        let p1_card_h = 48.0;
        draw_rectangle(p1_card_x, p1_card_y, p1_card_w, p1_card_h, Color::new(26.0 / 255.0, 32.0 / 255.0, 46.0 / 255.0, 1.0));
        draw_rectangle_lines(p1_card_x, p1_card_y, p1_card_w, p1_card_h, 1.5, COLOR_P1);

        let p1_label = format!("P1 [{}]", p1_type.to_uppercase());
        draw_text(&p1_label, p1_card_x + 12.0, p1_card_y + 20.0, 17.0, COLOR_P1);

        let p1_led = if p1_detected { COLOR_STATUS_ACTIVE } else { COLOR_STATUS_INACTIVE };
        draw_circle(p1_card_x + 16.0, p1_card_y + 34.0, 4.0, p1_led);
        let p1_status = if p1_detected { "CONECTADO" } else { "BUSCANDO..." };
        draw_text(p1_status, p1_card_x + 28.0, p1_card_y + 38.0, 14.0, COLOR_TEXT_MUTED);

        // 2. Center: Exterior Camera Box in Dashboard Frame
        let cam_target_w = 200.0;
        let cam_target_h = 114.0;
        let cam_x = (screen_w / 2.0) - (cam_target_w / 2.0);
        let cam_y = 16.0;

        let cam_bezel_pad = 3.0;
        draw_rectangle(
            cam_x - cam_bezel_pad,
            cam_y - cam_bezel_pad,
            cam_target_w + (cam_bezel_pad * 2.0),
            cam_target_h + (cam_bezel_pad * 2.0),
            Color::new(12.0 / 255.0, 16.0 / 255.0, 24.0 / 255.0, 1.0),
        );
        draw_rectangle_lines(
            cam_x - cam_bezel_pad,
            cam_y - cam_bezel_pad,
            cam_target_w + (cam_bezel_pad * 2.0),
            cam_target_h + (cam_bezel_pad * 2.0),
            2.0,
            Color::new(60.0 / 255.0, 80.0 / 255.0, 110.0 / 255.0, 1.0),
        );

        if let Some(tex) = preview_texture {
            draw_texture_ex(
                tex,
                cam_x,
                cam_y,
                WHITE,
                DrawTextureParams {
                    dest_size: Some(vec2(cam_target_w, cam_target_h)),
                    ..Default::default()
                },
            );
        } else {
            let load_str = "INICIANDO CÁMARA...";
            let font_size = 14.0;
            let m = measure_text(load_str, None, font_size as u16, 1.0);
            draw_text(
                load_str,
                cam_x + (cam_target_w / 2.0) - (m.width / 2.0),
                cam_y + (cam_target_h / 2.0) + (m.height / 2.0),
                font_size,
                Color::new(100.0 / 255.0, 130.0 / 255.0, 170.0 / 255.0, 1.0),
            );
        }

        // 3. Right Block: Player 2 Badge & Telemetry
        let p2_card_w = 210.0;
        let p2_card_h = 48.0;
        let p2_card_x = screen_w - 36.0 - p2_card_w;
        let p2_card_y = 72.0;

        draw_rectangle(p2_card_x, p2_card_y, p2_card_w, p2_card_h, Color::new(26.0 / 255.0, 32.0 / 255.0, 46.0 / 255.0, 1.0));
        draw_rectangle_lines(p2_card_x, p2_card_y, p2_card_w, p2_card_h, 1.5, COLOR_P2);

        let p2_label = format!("P2 [{}]", p2_type.to_uppercase());
        draw_text(&p2_label, p2_card_x + 12.0, p2_card_y + 20.0, 17.0, COLOR_P2);

        let p2_led = if p2_detected { COLOR_STATUS_ACTIVE } else { COLOR_STATUS_INACTIVE };
        draw_circle(p2_card_x + 16.0, p2_card_y + 34.0, 4.0, p2_led);
        let p2_status = if p2_detected { "CONECTADO" } else { "BUSCANDO..." };
        draw_text(p2_status, p2_card_x + 28.0, p2_card_y + 38.0, 14.0, COLOR_TEXT_MUTED);

        let rule_str = "PRIMERO A 5 PUNTOS";
        let rule_m = measure_text(rule_str, None, 16, 1.0);
        draw_text(rule_str, screen_w - 36.0 - rule_m.width, 36.0, 16.0, COLOR_TEXT_MUTED);

        let fps_str = format!("GAME: {:4.1} FPS | CV: {:4.1} FPS", game_fps, cv_fps);
        let fps_m = measure_text(&fps_str, None, 15, 1.0);
        draw_text(&fps_str, screen_w - 36.0 - fps_m.width, 56.0, 15.0, Color::new(110.0 / 255.0, 130.0 / 255.0, 155.0 / 255.0, 1.0));
    }

    pub fn draw_court(
        arena_x: f32,
        arena_y: f32,
        arena_w: f32,
        arena_h: f32,
        p1_score: u32,
        p2_score: u32,
    ) {
        // Court background & border
        draw_rectangle(arena_x, arena_y, arena_w, arena_h, COLOR_COURT_BG);
        draw_rectangle_lines(arena_x, arena_y, arena_w, arena_h, 3.0, COLOR_COURT_BORDER);

        // Dashed center net
        let center_x = arena_x + (arena_w / 2.0);
        let mut net_y = arena_y + 10.0;
        let net_end_y = arena_y + arena_h - 10.0;
        while net_y < net_end_y {
            let seg_end = (net_y + 16.0).min(net_end_y);
            draw_line(center_x, net_y, center_x, seg_end, 3.0, COLOR_NET);
            net_y += 26.0;
        }

        // Scores displayed prominently inside court
        let p1_str = p1_score.to_string();
        let p1_m = measure_text(&p1_str, None, 72, 1.0);
        draw_text(
            &p1_str,
            center_x - 140.0 - (p1_m.width / 2.0),
            arena_y + 72.0,
            72.0,
            COLOR_P1,
        );

        let p2_str = p2_score.to_string();
        let p2_m = measure_text(&p2_str, None, 72, 1.0);
        draw_text(
            &p2_str,
            center_x + 140.0 - (p2_m.width / 2.0),
            arena_y + 72.0,
            72.0,
            COLOR_P2,
        );
    }

    pub fn draw_footer_help(screen_w: f32, screen_h: f32) {
        let hints = "[ESPACIO] Iniciar / Pausa  |  [C] Recalibrar Centro Facial  |  [R] Reiniciar Partida  |  [ESC] Salir";
        let m = measure_text(hints, None, 14, 1.0);
        draw_text(
            hints,
            (screen_w / 2.0) - (m.width / 2.0),
            screen_h - 10.0,
            14.0,
            COLOR_TEXT_MUTED,
        );
    }
}
