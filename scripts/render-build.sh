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
export VENV_PATH=/opt/render/project/src/crawler/cj/venv

# Create virtual environment in a known location
cd crawler/cj

echo "Creating Python virtual environment at $VENV_PATH..."
python3 -m venv $VENV_PATH

echo "Installing Python dependencies in virtual environment..."
$VENV_PATH/bin/pip install --upgrade pip
$VENV_PATH/bin/pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers to $PLAYWRIGHT_BROWSERS_PATH..."
$VENV_PATH/bin/playwright install chromium

echo ""
echo "=== Verifying Installation ==="
echo "Python path: $VENV_PATH/bin/python"
echo "Python version:"
$VENV_PATH/bin/python --version

echo ""
echo "Installed packages:"
$VENV_PATH/bin/pip list | grep -E "(playwright|supabase|beautifulsoup4)" || echo "Warning: Some packages may not be installed"

echo ""
echo "Testing Playwright import:"
$VENV_PATH/bin/python -c "from playwright.async_api import async_playwright; print('✓ Playwright imported successfully')" || echo "✗ Playwright import failed!"

echo ""
echo "=== Build completed successfully ==="
