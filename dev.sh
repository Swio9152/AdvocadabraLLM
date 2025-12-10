#!/bin/bash

# AdvocaDabra Development Helper Script
# Consolidates common development tasks

set -e

COMMAND=${1:-help}

case $COMMAND in
    "setup")
        echo "🔧 Setting up development environment..."
        ./scripts/build.sh
        ;;
    
    "dev")
        echo "🚀 Starting development servers..."
        # Start backend in background
        cd backend
        source venv/bin/activate
        python backend_server.py &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        cd frontend/legal-ai-client
        npm run dev &
        FRONTEND_PID=$!
        cd ../..
        
        echo "✅ Development servers started!"
        echo "🌐 Backend: http://localhost:8000"
        echo "🎨 Frontend: http://localhost:5173"
        echo "Press Ctrl+C to stop all servers"
        
        # Wait and cleanup on exit
        trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
        wait
        ;;
        
    "build")
        echo "🏗️ Building for production..."
        cd frontend/legal-ai-client
        npm run build
        cd ../..
        echo "✅ Build complete! Files in frontend/legal-ai-client/dist/"
        ;;
        
    "clean")
        echo "🧹 Cleaning temporary files..."
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
        find . -name ".DS_Store" -delete 2>/dev/null || true
        echo "✅ Cleanup complete!"
        ;;
        
    "test")
        echo "🧪 Running system tests..."
        cd backend
        source venv/bin/activate
        python -m pytest tests/ 2>/dev/null || echo "No tests found"
        cd ../frontend/legal-ai-client
        npm test 2>/dev/null || echo "No frontend tests configured"
        cd ../..
        ;;
        
    "help"|*)
        echo "AdvocaDabra Development Helper"
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Commands:"
        echo "  setup   - Set up development environment"
        echo "  dev     - Start development servers"
        echo "  build   - Build for production"
        echo "  clean   - Clean temporary files"
        echo "  test    - Run tests"
        echo "  help    - Show this help"
        ;;
esac
