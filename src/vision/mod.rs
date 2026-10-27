pub mod camera;
pub mod detector;
pub mod smoother;

pub use camera::{CameraSystem, VisionFrame};
pub use detector::{FaceDetection, HeadTracker};
pub use smoother::EMASmoother;
