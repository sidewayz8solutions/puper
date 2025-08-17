#!/bin/bash

# Puper API Startup Script

echo "🚽 Starting Puper API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running again."
    exit 1
fi

# Validate configuration
echo "🔍 Validating configuration..."
if command -v python3 &> /dev/null; then
    python3 validate_config.py
    if [ $? -ne 0 ]; then
        echo "❌ Configuration validation failed. Please fix the issues above."
        exit 1
    fi
else
    echo "⚠️  Python3 not found, skipping configuration validation"
fi

# Check if Docker is available
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up -d
    echo "✅ Services started!"
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔍 Alternative docs: http://localhost:8000/redoc"
    echo "🗄️  Database: PostgreSQL on port 5432"
    echo "🔴 Redis: Redis on port 6379"
else
    echo "⚠️  Docker Compose not found. Please install Docker or run manually."
    echo "📋 Manual setup instructions:"
    echo "   1. Install dependencies: pip install -r requirements.txt"
    echo "   2. Setup PostgreSQL with PostGIS"
    echo "   3. Setup Redis"
    echo "   4. Configure .env file"
    echo "   5. Run: uvicorn main:app --reload"
fi
