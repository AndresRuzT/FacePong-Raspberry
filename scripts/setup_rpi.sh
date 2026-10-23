#!/usr/bin/env bash
# ==============================================================================
# FacePong — Raspberry Pi 4 Automated Setup Script
# Designed for Raspberry Pi OS (Bookworm) 64-bit (aarch64)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "   FacePong: Automated Setup for Raspberry Pi 4 (ARM64)   "
echo "=========================================================="

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "aarch64" ]; then
    echo "⚠️ Warning: Detected architecture '$ARCH'. FacePong is optimized for aarch64 (64-bit)."
    echo "Continuing setup..."
fi

# 1. Update and install system dependencies
echo "📦 Step 1: Installing essential system dependencies via apt..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libgl1-mesa-glx \
    libegl1-mesa \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    v4l-utils

# 2. Add current user to video group for camera device access
echo "📹 Step 2: Ensuring user '$(whoami)' has permission to access /dev/video*..."
sudo usermod -aG video "$(whoami)" || true

# 3. Create virtual environment
echo "🐍 Step 3: Creating Python 3.11 virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 4. Activate and upgrade pip
echo "🚀 Step 4: Upgrading pip and installing wheels inside virtual environment..."
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

# 5. Install FacePong and runtime dependencies
echo "🎮 Step 5: Installing FacePong dependencies..."
pip install -r requirements.txt
pip install -e .

echo ""
echo "=========================================================="
echo "✅ Installation completed successfully!"
echo "=========================================================="
echo "To run the game:"
echo "  1. source .venv/bin/activate"
echo "  2. python3 -m facepong.main"
echo ""
echo "To test with keyboard controls (no camera needed):"
echo "  python3 -m facepong.main --keyboard"
echo "=========================================================="
