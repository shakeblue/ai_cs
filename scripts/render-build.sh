#!/bin/bash
set -e

echo "=== Render Build Script ==="
echo "Installing Node.js dependencies..."

# Install backend Node.js dependencies
cd backend
npm install --production=false
cd ..

echo "=== Setting up Python crawler ==="

# Set up paths for Render environment
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/.cache/ms-playwright

# Install Python dependencies globally (Render provides Python)
cd crawler/cj

echo "Installing Python dependencies..."
pip3 install --user --upgrade pip
pip3 install --user -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers to $PLAYWRIGHT_BROWSERS_PATH..."
python3 -m playwright install chromium

# Verify installation
echo "Verifying Playwright installation..."
python3 -m playwright install-deps || echo "Note: System deps may require manual installation"

echo "=== Build completed successfully ==="
