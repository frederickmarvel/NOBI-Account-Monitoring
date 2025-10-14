#!/bin/bash

# Blockchain Monitoring - Start Script
# This script starts the Python Flask backend

echo "🚀 Starting Blockchain Monitoring System..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    exit 1
fi

# Load PORT from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

PORT=${PORT:-8085}

# Install dependencies if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    echo "📦 Checking Python dependencies..."
    pip3 install -q -r backend/requirements.txt
    echo "✅ Dependencies ready"
    echo ""
fi

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT is already in use"
    echo "Killing existing process..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start Python backend
echo "🐍 Starting Python Flask backend on port $PORT..."
cd backend && python3 backend.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo ""
echo "✨ System is ready!"
echo ""
echo "📊 Frontend: Open frontend/index.html in browser"
echo "🔌 API Endpoint: http://localhost:$PORT/api"
echo ""
echo "🧪 Test with:"
echo "   curl http://localhost:$PORT/api/health"
echo ""
echo "📝 Active test address (Binance Hot Wallet):"
echo "   0x28C6c06298d514Db089934071355E5743bf21d60"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser (macOS)
if command -v open &> /dev/null; then
    sleep 2
    open "frontend/index.html" 2>/dev/null &
fi

# Wait for backend process
wait $BACKEND_PID
