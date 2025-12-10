#!/bin/bash

# AdvocaDabra Build Script
# Consolidates setup and build tasks

set -e

echo "🚀 AdvocaDabra Legal AI Build Script"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ Node.js/npm is required but not installed."
    exit 1
fi

# Backend setup
echo "🔧 Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo "🎨 Setting up frontend..."
cd frontend/legal-ai-client

echo "Installing Node.js dependencies..."
npm install

echo "Building frontend..."
npm run build

cd ../..

echo "✅ Build completed successfully!"
echo "🎯 To start the system, run: ./start_system.sh"
