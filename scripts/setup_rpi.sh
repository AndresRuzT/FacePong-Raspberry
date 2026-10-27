#!/usr/bin/env bash
# ==============================================================================
# FacePong — Raspberry Pi 4 Automated Setup Script (Rust Engine)
# Compatible with Debian 12 (Bookworm) and Debian 13 (Trixie) 64-bit (aarch64)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "   FacePong: Automated Setup for Raspberry Pi 4 (ARM64)   "
echo "   High-Performance Native Rust Engine (Macroquad + V4L2) "
echo "=========================================================="

ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "[!] Note: Detected architecture '$ARCH'. FacePong is optimized for aarch64 (64-bit)."
    echo "Continuing setup..."
fi

# 1. Install system build dependencies and runtime libraries
echo "[*] Step 1: Installing essential system dependencies via apt..."
sudo apt update
sudo apt install -y \
    curl \
    build-essential \
    pkg-config \
    libgl1 \
    libegl1 \
    libasound2-dev \
    libv4l-dev \
    libx11-dev \
    libxi-dev \
    v4l-utils

# 2. Add current user to video group for camera device access
echo "[*] Step 2: Ensuring user '$(whoami)' has permission to access /dev/video*..."
sudo usermod -aG video "$(whoami)" || true

# 3. Install Rust toolchain if not installed
echo "[*] Step 3: Checking Rust toolchain..."
if ! command -v cargo &> /dev/null; then
    echo "[*] Rust not found. Installing stable Rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "[+] Rust toolchain is already installed ($(cargo --version))."
fi

# 4. Build high-performance release binary
echo "[*] Step 4: Compiling FacePong in release mode with NEON SIMD and LTO..."
source "$HOME/.cargo/env" || true
cargo build --release

echo ""
echo "=========================================================="
echo "[+] Build and setup completed successfully!"
echo "=========================================================="
echo "To run FacePong:"
echo "  ./target/release/facepong"
echo ""
echo "Controls:"
echo "  [ESPACIO] Iniciar Partida / Pausar / Continuar"
echo "  [C]       Recalibrar Centro Facial"
echo "  [R]       Reiniciar Marcador"
echo "  [W / S]   Control manual Paleta Izquierda (P1)"
echo "  [Arriba / Abajo] Control manual Paleta Derecha (P2)"
echo "  [ESC]     Salir"
echo "=========================================================="
