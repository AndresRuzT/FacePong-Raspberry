# FacePong User Guide: How to Play and Enjoy

Welcome to FacePong, an interactive arcade experience where your head movement directly guides the paddle on screen. Whether you are demonstrating this at an exhibition, using it in an academic laboratory, or having fun with friends, this guide walks you through every step to get the best possible experience.

## What You Need Before Starting

To enjoy FacePong at its full potential, make sure you have the following ready:

1. A Raspberry Pi 4 Model B or a modern personal computer running Linux.
2. A standard USB webcam placed securely on top of or just below your display.
3. An HDMI screen or monitor with at least 1280 by 720 resolution.
4. A room with clear, even front lighting so the camera can clearly see your face without heavy shadows.

## Quick Start: Launching the Game

You can run FacePong using either the high performance native Rust engine or the Python reference engine.

### Launching with Rust (Recommended for Raspberry Pi)

Open your terminal and run the compiled release build:

```bash
cargo run --release
```

If you previously ran the setup script, you can also execute the binary directly:

```bash
./target/release/facepong
```

### Launching with Python (Ideal for Desktop Experimentation)

Activate your virtual environment and start the Python version:

```bash
source .venv/bin/activate
python -m facepong.main
```

## Camera Setup and Player Positioning

FacePong uses a single USB camera to track both participants at the same time:

1. Sit or stand side by side in front of the screen, roughly two to three feet away from the lens.
2. Player 1 sits on the left side of the camera view and controls the cyan paddle.
3. Player 2 sits on the right side of the camera view and controls the amber paddle.
4. Look at the live camera preview box located on the upper dashboard. You should see a rectangular tracking box around each player face.
5. Make sure neither player blocks the other and avoid bright lamps or sunny windows directly behind you.

## In Game Controls and Keyboard Shortcuts

Every core function can be controlled quickly using your keyboard:

1. Start or Pause: Press the Space bar to begin the match or pause the action at any moment.
2. Calibrate Neutral Center: Press the C key while sitting upright and looking straight ahead. This immediately sets your natural resting posture as the center of the court.
3. Reset Match: Press the R key to reset both scores to zero and begin a fresh round.
4. Manual Keyboard Control for Player 1: Use the W key to glide upward and the S key to glide downward.
5. Manual Keyboard Control for Player 2: Use the Up Arrow to glide upward and the Down Arrow to glide downward.
6. Exit the Application: Press the Escape key at any time to close the game smoothly.

## How to Play Like a Champion

1. Gentle Movements: The vision algorithm is sensitive and responsive. Small, deliberate tilts of your chin up and down will move your paddle across the entire court.
2. Natural Calibration: Whenever you change your sitting posture or switch players, press the C key to calibrate immediately. This ensures your resting posture feels completely effortless.
3. Curve the Ball: Striking the ball near the outer edges of your paddle angles the ball sharply, making it harder for your opponent to return.
4. Speed Escalation: Each time a paddle deflects the ball, the ball gains extra speed. Keep your focus sharp during long rallies.

## Customizing Game Settings

FacePong includes a readable configuration file located at config/default.toml. You can open this file in any text editor to adjust settings such as:

1. Winning score: Change winning_score to set shorter or longer matches.
2. Paddle dimensions: Increase paddle_height if you prefer an easier game for younger players.
3. Motion sensitivity: Adjust sensitivity to increase or decrease how far the paddle travels when you tilt your head.

## Troubleshooting Common Questions

1. What if my camera is not detected?
Verify that your webcam is plugged in and recognized by your system by running v4l2ctl list devices in your terminal. Ensure your user account belongs to the video group.

2. What if the paddle jitters or stays stuck?
Check your room lighting. Overhead lights or side lamps might create harsh shadows on your cheeks. Facing a soft light source gives the color segmentation algorithm clean skin tones to track.

3. Can one person play alone?
Yes. You can test your skills on one side while controlling the other paddle manually with the keyboard, or simply invite a friend to step in.

Have fun playing FacePong!
