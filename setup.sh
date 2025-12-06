#!/bin/bash

# AdvocaDabra Legal AI - Complete Setup Script
# This script sets up the entire development environment

set -e

echo "🏛️  AdvocaDabra Legal AI - Complete Setup"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the AdvocadabraLLM root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔍 Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python 3 found: $PYTHON_VERSION"

# Check Node.js
if ! command_exists node; then
    echo "❌ Error: Node.js is required but not installed."
    echo "   Please install Node.js 16+ and try again."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js found: $NODE_VERSION"

# Check npm
if ! command_exists npm; then
    echo "❌ Error: npm is required but not installed."
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm found: $NPM_VERSION"

echo ""
echo "🔧 Setting up backend..."
echo "========================"

cd backend

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in backend directory"
    exit 1
fi

pip3 install -r requirements.txt

# Generate development environment
echo "🗃️  Generating development data files..."
python3 setup_dev_environment.py

# Create test user if database doesn't exist
if [ ! -f "users.db" ]; then
    echo "👤 Creating test user..."
    python3 -c "
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password_hash TEXT)''')

# Create test user
email = 'test@example.com'
password = 'test123'
name = 'Test User'
password_hash = generate_password_hash(password)

try:
    c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
              (name, email, password_hash))
    conn.commit()
    print('✅ Test user created successfully')
except sqlite3.IntegrityError:
    print('✅ Test user already exists')
finally:
    conn.close()
"
fi

cd ..

echo ""
echo "🎨 Setting up frontend..."
echo "========================"

cd frontend/legal-ai-client

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in frontend directory"
    exit 1
fi

npm install

cd ../..

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "1. Start Backend Server:"
echo "   cd backend && python3 backend_server.py"
echo ""
echo "2. Start Frontend Server (in new terminal):"
echo "   cd frontend/legal-ai-client && npm run dev"
echo ""
echo "3. Or use the convenience script:"
echo "   ./start_system.sh"
echo ""
echo "📱 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000/api"
echo ""
echo "🔐 Test Login Credentials:"
echo "   Email:    test@example.com"
echo "   Password: test123"
echo ""
echo "✨ Features Available:"
echo "   🔍 Similar Case Retrieval (SCR)"
echo "   📚 Precedent Case Retrieval (PCR)" 
echo "   📤 File Upload & Analysis"
echo "   🔐 User Authentication"
echo ""
echo "🎊 AdvocaDabra Legal AI is ready for development!"
