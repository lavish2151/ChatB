#!/bin/bash
# Build script for Render deployment
set -e

echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "Building React app..."
cd ../snackbot-web
npm install
npm run build
cd ../snackbot-api

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"
