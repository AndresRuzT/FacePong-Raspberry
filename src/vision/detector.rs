use crate::vision::smoother::EMASmoother;

#[derive(Debug, Clone, Copy)]
pub struct FaceDetection {
    pub detected: bool,
    pub norm_y: f32,
    pub bbox: (u32, u32, u32, u32), // (x, y, w, h) in subframe coords
}

#[derive(Debug, Clone)]
pub struct HeadTracker {
    pub sensitivity: f32,
    pub upward_gain: f32,
    pub invert: bool,
    smoother: EMASmoother,
    neutral_y: Option<f32>,
    calibration_samples: Vec<f32>,
}

impl HeadTracker {
    pub fn new(sensitivity: f32, upward_gain: f32, alpha: f32, invert: bool) -> Self {
        Self {
            sensitivity,
            upward_gain,
            invert,
            smoother: EMASmoother::new(alpha, 0.005, 0.65),
            neutral_y: Some(0.5),
            calibration_samples: Vec::with_capacity(10),
        }
    }

    pub fn recalibrate(&mut self) {
        self.neutral_y = None;
        self.calibration_samples.clear();
        self.smoother.reset();
    }

    /// Process a subframe slice of RGB pixels and extract vertical normalized head position.
    /// `subframe_rgb` is a slice of RGB24 bytes with dimensions `(sub_w, sub_h)`.
    pub fn process_subframe(
        &mut self,
        subframe_rgb: &[u8],
        sub_w: u32,
        sub_h: u32,
        stride: u32,
    ) -> FaceDetection {
        let total_pixels = (sub_w * sub_h) as f32;
        let mut m00: u32 = 0;
        let mut m01: u64 = 0;

        let mut min_x = sub_w;
        let mut max_x = 0;
        let mut min_y = sub_h;
        let mut max_y = 0;

        // Fast downsampled scan (step by 2 in x and y for extreme speed on Cortex-A72)
        let step = 2usize;
        for y in (0..sub_h).step_by(step) {
            let row_offset = (y * stride * 3) as usize;
            for x in (0..sub_w).step_by(step) {
                let px = row_offset + (x as usize * 3);
                if px + 2 >= subframe_rgb.len() {
                    break;
                }
                let r = subframe_rgb[px] as i32;
                let g = subframe_rgb[px + 1] as i32;
                let b = subframe_rgb[px + 2] as i32;

                // Fixed-point YCbCr skin detection:
                // Cb in [77, 127], Cr in [133, 173]
                let cb = 128 + ((-173 * r - 339 * g + 512 * b) >> 10);
                let cr = 128 + ((512 * r - 429 * g - 83 * b) >> 10);

                if (77..=127).contains(&cb) && (133..=173).contains(&cr) {
                    m00 += 1;
                    m01 += y as u64;

                    if x < min_x { min_x = x; }
                    if x > max_x { max_x = x; }
                    if y < min_y { min_y = y; }
                    if y > max_y { max_y = y; }
                }
            }
        }

        let sampled_pixels = total_pixels / ((step * step) as f32);
        let min_required = (sampled_pixels * 0.02) as u32; // Minimum 2% skin coverage

        if m00 < min_required || min_x >= max_x || min_y >= max_y {
            return FaceDetection {
                detected: false,
                norm_y: 0.5,
                bbox: (0, 0, 0, 0),
            };
        }

        let cy_px = (m01 as f32) / (m00 as f32);
        let norm_cy = cy_px / (sub_h as f32);

        // Auto-calibration: calibrate resting posture
        if self.neutral_y.is_none() {
            self.calibration_samples.push(norm_cy);
            if self.calibration_samples.len() >= 6 {
                let avg = self.calibration_samples.iter().sum::<f32>()
                    / (self.calibration_samples.len() as f32);
                self.neutral_y = Some(avg);
            } else {
                self.neutral_y = Some(norm_cy);
            }
        }

        let baseline = self.neutral_y.unwrap_or(0.5);
        let deviation = norm_cy - baseline;

        // Biomechanical gain compensation:
        // Neck flexion/extension has unequal biomechanical limits and looking up foreshortens face.
        let gain = if deviation < 0.0 {
            self.upward_gain
        } else {
            1.20
        };

        let mut target_norm = 0.5 + (deviation * gain * self.sensitivity);
        if self.invert {
            target_norm = 1.0 - target_norm;
        }
        let clamped = target_norm.clamp(0.0, 1.0);
        let smoothed = self.smoother.filter(clamped);

        let bw = (max_x - min_x).max(1);
        let bh = (max_y - min_y).max(1);

        FaceDetection {
            detected: true,
            norm_y: smoothed,
            bbox: (min_x, min_y, bw, bh),
        }
    }
}
