# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core Pong engine with continuous float coordinates, delta-time integration and velocity scaling.
- Computer Vision subsystem using MediaPipe Face Mesh (`model_complexity=0`).
- Dual-player camera splitter (horizontal split) on single USB webcam.
- Inter-process communication via lock-free freshest-frame queues.
- Exponential Moving Average (EMA) signal smoothing and deadzone filtering.
- Input abstraction layer decoupling input sources (Face vs Keyboard) from game logic.
- Configurable TOML loader with strongly typed dataclasses.
- Minimalist academic HUD displaying match score, framerate, and player detection indicators.
- Automated CI pipeline with Ruff, Mypy, and Pytest coverage suite.
