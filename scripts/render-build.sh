#!/bin/bash
set -e

echo "=== Render Build Script ==="
echo "Installing Node.js dependencies..."

# Install backend Node.js dependencies
cd backend
npm install --production=false
cd ..

echo "=== Setting up Python crawler ==="

# Install Python and create virtual environment
cd crawler/cj

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium

deactivate

echo "=== Build completed successfully ==="
