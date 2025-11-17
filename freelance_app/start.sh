#!/bin/bash

# AI Freelance Search App - Quick Start Script

echo "🚀 AI Freelance Search App - Quick Start"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp ../.env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo ""
    echo "Required:"
    echo "  - GROQ_API_KEY"
    echo "  - SECRET_KEY (generate a random string)"
    echo ""
    read -p "Press Enter to continue after editing .env..."
fi

# Check if GROQ_API_KEY is set
source .env
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not set in .env file"
    exit 1
fi

echo ""
echo "Choose deployment method:"
echo "1. Docker Compose (recommended)"
echo "2. Local development"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "🐳 Starting with Docker Compose..."

    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose not found. Please install Docker and Docker Compose."
        exit 1
    fi

    # Build and start containers
    docker-compose up --build -d

    echo ""
    echo "✅ Application started!"
    echo ""
    echo "Services:"
    echo "  - API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"

elif [ "$choice" = "2" ]; then
    echo ""
    echo "💻 Starting local development..."

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.11+."
        exit 1
    fi

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Check if PostgreSQL is running
    echo "Checking PostgreSQL..."
    if ! pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "⚠️  PostgreSQL not running on localhost:5432"
        echo "Please start PostgreSQL or use Docker Compose."
        exit 1
    fi

    # Initialize database
    echo "Initializing database..."
    python database/init_db.py create
    python database/init_db.py seed

    # Start application
    echo ""
    echo "🚀 Starting application..."
    python main.py

else
    echo "❌ Invalid choice"
    exit 1
fi
