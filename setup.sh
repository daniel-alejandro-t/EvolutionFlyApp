#!/bin/bash

# Evolution Fly App - Development Setup Script

echo "🛫 Evolution Fly App - Setting up development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env .env
    echo "Please edit .env file with your configurations!"
fi

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Load initial destinations
echo "🌍 Loading initial destinations..."
python manage.py load_destinations

# Create superuser (optional)
read -p "Do you want to create a superuser? (y/N): " create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Frontend setup
if [ -d "frontend" ]; then
    echo "⚛️ Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
    fi
    
    if [ ! -f ".env" ]; then
        echo "⚙️ Creating frontend .env file..."
        echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
    fi
    
    cd ..
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development servers:"
echo "   Backend:  python manage.py runserver"
echo "   Frontend: cd frontend && npm start"
echo "   Celery:   celery -A evolutionflyapp worker --loglevel=info"
echo "   Beat:     celery -A evolutionflyapp beat --loglevel=info"
echo ""
echo "🌐 URLs:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   Admin:    http://localhost:8000/admin"