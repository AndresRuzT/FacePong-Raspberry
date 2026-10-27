use crate::config::VisionConfig;
use crate::vision::detector::HeadTracker;
use crossbeam_channel::{bounded, Receiver, Sender};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

#[derive(Clone, Debug)]
pub struct VisionFrame {
    pub p1_detected: bool,
    pub p2_detected: bool,
    pub p1_norm_y: f32,
    pub p2_norm_y: f32,
    pub p1_bbox: (u32, u32, u32, u32),
    pub p2_bbox: (u32, u32, u32, u32),
    pub cv_fps: f32,
    pub rgba_data: Vec<u8>,
    pub width: u32,
    pub height: u32,
}

pub struct CameraSystem {
    pub receiver: Receiver<VisionFrame>,
    pub recalibrate_tx: Sender<()>,
    stop_flag: Arc<AtomicBool>,
}

impl CameraSystem {
    pub fn start(config: VisionConfig) -> Self {
        let (tx, rx) = bounded::<VisionFrame>(1);
        let (recal_tx, recal_rx) = bounded::<()>(4);
        let stop_flag = Arc::new(AtomicBool::new(false));
        let thread_stop = Arc::clone(&stop_flag);

        thread::spawn(move || {
            run_vision_loop(config, tx, recal_rx, thread_stop);
        });

        Self {
            receiver: rx,
            recalibrate_tx: recal_tx,
            stop_flag,
        }
    }

    pub fn recalibrate(&self) {
        let _ = self.recalibrate_tx.try_send(());
    }
}

impl Drop for CameraSystem {
    fn drop(&mut self) {
        self.stop_flag.store(true, Ordering::Relaxed);
    }
}

fn run_vision_loop(
    config: VisionConfig,
    tx: Sender<VisionFrame>,
    recal_rx: Receiver<()>,
    stop_flag: Arc<AtomicBool>,
) {
    let width = config.frame_width;
    let height = config.frame_height;

    let mut tracker1 = HeadTracker::new(
        config.sensitivity,
        config.upward_gain,
        config.smoothing_alpha,
        false,
    );
    let mut tracker2 = HeadTracker::new(
        config.sensitivity,
        config.upward_gain,
        config.smoothing_alpha,
        false,
    );

    #[cfg(target_os = "linux")]
    {
        if let Ok(mut capture) = LinuxV4LCapture::open(config.camera_index, width, height) {
            let mut last_fps_time = Instant::now();
            let mut frame_count = 0u32;
            let mut cv_fps = 0.0f32;
            let mut rgb_buffer = vec![0u8; (width * height * 3) as usize];
            let mut rgba_buffer = vec![255u8; (width * height * 4) as usize];

            while !stop_flag.load(Ordering::Relaxed) {
                if recal_rx.try_recv().is_ok() {
                    tracker1.recalibrate();
                    tracker2.recalibrate();
                }

                if capture.read_frame(&mut rgb_buffer).is_ok() {
                    process_and_send(
                        &rgb_buffer,
                        &mut rgba_buffer,
                        width,
                        height,
                        &mut tracker1,
                        &mut tracker2,
                        &mut frame_count,
                        &mut last_fps_time,
                        &mut cv_fps,
                        &tx,
                    );
                } else {
                    thread::sleep(std::time::Duration::from_millis(5));
                }
            }
            return;
        }
    }

    // Fallback: simulated camera loop (when /dev/video0 is not accessible or on test systems)
    run_mock_vision_loop(
        width,
        height,
        &mut tracker1,
        &mut tracker2,
        tx,
        recal_rx,
        stop_flag,
    );
}

fn process_and_send(
    rgb: &[u8],
    rgba: &mut [u8],
    width: u32,
    height: u32,
    tracker1: &mut HeadTracker,
    tracker2: &mut HeadTracker,
    frame_count: &mut u32,
    last_fps_time: &mut Instant,
    cv_fps: &mut f32,
    tx: &Sender<VisionFrame>,
) {
    let half_w = width / 2;

    // Subframe 1: Left half (Player 1)
    let mut sub1 = vec![0u8; (half_w * height * 3) as usize];
    for y in 0..height {
        let src_row = (y * width * 3) as usize;
        let dst_row = (y * half_w * 3) as usize;
        sub1[dst_row..dst_row + (half_w * 3) as usize]
            .copy_from_slice(&rgb[src_row..src_row + (half_w * 3) as usize]);
    }

    // Subframe 2: Right half (Player 2)
    let mut sub2 = vec![0u8; (half_w * height * 3) as usize];
    for y in 0..height {
        let src_row = ((y * width + half_w) * 3) as usize;
        let dst_row = (y * half_w * 3) as usize;
        sub2[dst_row..dst_row + (half_w * 3) as usize]
            .copy_from_slice(&rgb[src_row..src_row + (half_w * 3) as usize]);
    }

    let det1 = tracker1.process_subframe(&sub1, half_w, height, half_w);
    let det2 = tracker2.process_subframe(&sub2, half_w, height, half_w);

    // Populate RGBA preview buffer for GPU texture display
    for y in 0..height {
        for x in 0..width {
            let rgb_idx = ((y * width + x) * 3) as usize;
            let rgba_idx = ((y * width + x) * 4) as usize;

            rgba[rgba_idx] = rgb[rgb_idx];
            rgba[rgba_idx + 1] = rgb[rgb_idx + 1];
            rgba[rgba_idx + 2] = rgb[rgb_idx + 2];
            rgba[rgba_idx + 3] = 255;
        }
    }

    // Draw visual UI overlays directly onto preview buffer
    draw_center_divider(rgba, width, height);
    if det1.detected {
        draw_bounding_box(rgba, width, height, det1.bbox, (0, 220, 255));
    }
    if det2.detected {
        let offset_bbox = (det2.bbox.0 + half_w, det2.bbox.1, det2.bbox.2, det2.bbox.3);
        draw_bounding_box(rgba, width, height, offset_bbox, (255, 150, 20));
    }

    *frame_count += 1;
    let elapsed = last_fps_time.elapsed().as_secs_f32();
    if elapsed >= 0.5 {
        *cv_fps = (*frame_count as f32) / elapsed;
        *frame_count = 0;
        *last_fps_time = Instant::now();
    }

    let frame = VisionFrame {
        p1_detected: det1.detected,
        p2_detected: det2.detected,
        p1_norm_y: det1.norm_y,
        p2_norm_y: det2.norm_y,
        p1_bbox: det1.bbox,
        p2_bbox: det2.bbox,
        cv_fps: *cv_fps,
        rgba_data: rgba.to_vec(),
        width,
        height,
    };

    // Replace old frame if unread to maintain zero latency
    let _ = tx.try_send(frame);
}

fn draw_center_divider(rgba: &mut [u8], width: u32, height: u32) {
    let cx = width / 2;
    for y in (0..height).step_by(4) {
        let idx = ((y * width + cx) * 4) as usize;
        if idx + 3 < rgba.len() {
            rgba[idx] = 70;
            rgba[idx + 1] = 90;
            rgba[idx + 2] = 120;
            rgba[idx + 3] = 255;
        }
    }
}

fn draw_bounding_box(
    rgba: &mut [u8],
    width: u32,
    height: u32,
    bbox: (u32, u32, u32, u32),
    color: (u8, u8, u8),
) {
    let (bx, by, bw, bh) = bbox;
    let x_end = (bx + bw).min(width - 1);
    let y_end = (by + bh).min(height - 1);

    for x in bx..=x_end {
        let top_idx = ((by * width + x) * 4) as usize;
        let bot_idx = ((y_end * width + x) * 4) as usize;
        if top_idx + 3 < rgba.len() {
            rgba[top_idx] = color.0;
            rgba[top_idx + 1] = color.1;
            rgba[top_idx + 2] = color.2;
        }
        if bot_idx + 3 < rgba.len() {
            rgba[bot_idx] = color.0;
            rgba[bot_idx + 1] = color.1;
            rgba[bot_idx + 2] = color.2;
        }
    }

    for y in by..=y_end {
        let left_idx = ((y * width + bx) * 4) as usize;
        let right_idx = ((y * width + x_end) * 4) as usize;
        if left_idx + 3 < rgba.len() {
            rgba[left_idx] = color.0;
            rgba[left_idx + 1] = color.1;
            rgba[left_idx + 2] = color.2;
        }
        if right_idx + 3 < rgba.len() {
            rgba[right_idx] = color.0;
            rgba[right_idx + 1] = color.1;
            rgba[right_idx + 2] = color.2;
        }
    }
}

fn run_mock_vision_loop(
    width: u32,
    height: u32,
    tracker1: &mut HeadTracker,
    tracker2: &mut HeadTracker,
    tx: Sender<VisionFrame>,
    recal_rx: Receiver<()>,
    stop_flag: Arc<AtomicBool>,
) {
    let start_time = Instant::now();
    let mut frame_count = 0u32;
    let mut last_fps_time = Instant::now();
    let mut cv_fps = 30.0f32;
    let mut rgb = vec![16u8; (width * height * 3) as usize];
    let mut rgba = vec![255u8; (width * height * 4) as usize];

    while !stop_flag.load(Ordering::Relaxed) {
        if recal_rx.try_recv().is_ok() {
            tracker1.recalibrate();
            tracker2.recalibrate();
        }

        let t = start_time.elapsed().as_secs_f32();

        // Synthetic skin patches moving vertically
        rgb.fill(24);
        let p1_cy = ((height as f32 * 0.5) + (t * 1.5).sin() * 40.0) as u32;
        let p2_cy = ((height as f32 * 0.5) + ((t * 1.2) + 1.0).sin() * 40.0) as u32;

        render_mock_face(&mut rgb, width, height, width / 4, p1_cy, 24);
        render_mock_face(&mut rgb, width, height, (width * 3) / 4, p2_cy, 24);

        process_and_send(
            &rgb,
            &mut rgba,
            width,
            height,
            tracker1,
            tracker2,
            &mut frame_count,
            &mut last_fps_time,
            &mut cv_fps,
            &tx,
        );

        thread::sleep(std::time::Duration::from_millis(30));
    }
}

fn render_mock_face(rgb: &mut [u8], width: u32, height: u32, cx: u32, cy: u32, radius: u32) {
    let min_x = cx.saturating_sub(radius);
    let max_x = (cx + radius).min(width - 1);
    let min_y = cy.saturating_sub(radius);
    let max_y = (cy + radius).min(height - 1);

    for y in min_y..=max_y {
        for x in min_x..=max_x {
            let dx = (x as i32) - (cx as i32);
            let dy = (y as i32) - (cy as i32);
            if (dx * dx + dy * dy) <= (radius as i32 * radius as i32) {
                let idx = ((y * width + x) * 3) as usize;
                if idx + 2 < rgb.len() {
                    // Skin color in RGB: R=210, G=160, B=130
                    rgb[idx] = 210;
                    rgb[idx + 1] = 160;
                    rgb[idx + 2] = 130;
                }
            }
        }
    }
}

#[cfg(target_os = "linux")]
struct LinuxV4LCapture {
    stream: v4l::io::mmap::Stream<'static>,
    width: u32,
    height: u32,
    fourcc: v4l::format::fourcc::FourCC,
}

#[cfg(target_os = "linux")]
impl LinuxV4LCapture {
    pub fn open(
        camera_index: usize,
        req_w: u32,
        req_h: u32,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        use v4l::buffer::Type;
        use v4l::format::fourcc::FourCC;
        use v4l::video::Capture;
        use v4l::Device;

        let dev = Device::new(camera_index)?;
        let mut fmt = dev.format()?;
        fmt.width = req_w;
        fmt.height = req_h;
        // Prefer YUYV, fallback to device format
        fmt.fourcc = FourCC::new(b"YUYV");
        let active_fmt = dev.set_format(&fmt).unwrap_or(fmt);

        let stream = v4l::io::mmap::Stream::with_buffers(&dev, Type::VideoCapture, 3)?;
        // Leak device reference safety for 'static stream lifetime in background thread
        let leaked_stream: v4l::io::mmap::Stream<'static> = unsafe { std::mem::transmute(stream) };

        Ok(Self {
            stream: leaked_stream,
            width: active_fmt.width,
            height: active_fmt.height,
            fourcc: active_fmt.fourcc,
        })
    }

    pub fn read_frame(&mut self, out_rgb: &mut [u8]) -> Result<(), Box<dyn std::error::Error>> {
        use v4l::io::traits::CaptureStream;

        let (buf, _meta) = self.stream.next()?;

        if self.fourcc.repr == *b"YUYV" {
            decode_yuyv_mirrored(buf, out_rgb, self.width, self.height);
        } else if self.fourcc.repr == *b"MJPG" {
            if let Ok(img) = image::load_from_memory_with_format(buf, image::ImageFormat::Jpeg) {
                let rgb = img.to_rgb8();
                mirror_and_copy(rgb.as_raw(), out_rgb, self.width, self.height);
            }
        } else {
            mirror_and_copy(buf, out_rgb, self.width, self.height);
        }

        Ok(())
    }
}

/// Convert YUYV buffer to RGB24 while flipping horizontally in a single pass.
/// Direct mirrored conversion eliminates an extra full-frame copy and cache misses.
#[inline]
fn decode_yuyv_mirrored(yuyv: &[u8], rgb: &mut [u8], width: u32, height: u32) {
    let w = width as usize;
    let h = height as usize;

    for y in 0..h {
        let src_row = y * w * 2;
        let dst_row = y * w * 3;

        for x in (0..w).step_by(2) {
            let src_idx = src_row + (x * 2);
            if src_idx + 3 >= yuyv.len() {
                break;
            }

            let y0 = yuyv[src_idx] as i32;
            let u = yuyv[src_idx + 1] as i32;
            let y1 = yuyv[src_idx + 2] as i32;
            let v = yuyv[src_idx + 3] as i32;

            // Pixel 1: Y0, U, V
            let r0 = (y0 + ((1436 * (v - 128)) >> 10)).clamp(0, 255) as u8;
            let g0 = (y0 - ((352 * (u - 128) + 731 * (v - 128)) >> 10)).clamp(0, 255) as u8;
            let b0 = (y0 + ((1814 * (u - 128)) >> 10)).clamp(0, 255) as u8;

            // Pixel 2: Y1, U, V
            let r1 = (y1 + ((1436 * (v - 128)) >> 10)).clamp(0, 255) as u8;
            let g1 = (y1 - ((352 * (u - 128) + 731 * (v - 128)) >> 10)).clamp(0, 255) as u8;
            let b1 = (y1 + ((1814 * (u - 128)) >> 10)).clamp(0, 255) as u8;

            // Mirrored horizontal coordinates
            let mirror_x0 = w - 1 - x;
            let mirror_x1 = w - 2 - x;

            let dst_idx0 = dst_row + (mirror_x0 * 3);
            let dst_idx1 = dst_row + (mirror_x1 * 3);

            if dst_idx0 + 2 < rgb.len() {
                rgb[dst_idx0] = r0;
                rgb[dst_idx0 + 1] = g0;
                rgb[dst_idx0 + 2] = b0;
            }
            if dst_idx1 + 2 < rgb.len() {
                rgb[dst_idx1] = r1;
                rgb[dst_idx1 + 1] = g1;
                rgb[dst_idx1 + 2] = b1;
            }
        }
    }
}

#[inline]
fn mirror_and_copy(src: &[u8], dst: &mut [u8], width: u32, height: u32) {
    let w = width as usize;
    let h = height as usize;

    for y in 0..h {
        let src_row = y * w * 3;
        let dst_row = y * w * 3;
        for x in 0..w {
            let mirror_x = w - 1 - x;
            let s_idx = src_row + (x * 3);
            let d_idx = dst_row + (mirror_x * 3);
            if s_idx + 2 < src.len() && d_idx + 2 < dst.len() {
                dst[d_idx] = src[s_idx];
                dst[d_idx + 1] = src[s_idx + 1];
                dst[d_idx + 2] = src[s_idx + 2];
            }
        }
    }
}
