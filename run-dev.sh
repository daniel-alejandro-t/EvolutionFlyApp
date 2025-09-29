#!/bin/bash

# Evolution Fly App - Start Development Servers

echo "🛫 Starting Evolution Fly App development servers..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
if ! command_exists python; then
    echo "❌ Python is not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command_exists redis-server; then
    echo "⚠️ Redis is not installed. Installing with Docker..."
    docker run -d -p 6379:6379 redis:7-alpine
fi

# Start backend in background
echo "🚀 Starting Django backend..."
source venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

# Start frontend in background
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
celery -A evolutionflyapp worker --loglevel=info &
CELERY_PID=$!

# Start Celery beat in background
echo "⏰ Starting Celery beat..."
celery -A evolutionflyapp beat --loglevel=info &
BEAT_PID=$!

echo ""
echo "✅ All services started!"
echo "🌐 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo "   Celery:   $CELERY_PID"
echo "   Beat:     $BEAT_PID"
echo ""
echo "Press Ctrl+C to stop all services..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID $FRONTEND_PID $CELERY_PID $BEAT_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for all background processes
wait