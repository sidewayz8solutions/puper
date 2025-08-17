#!/bin/bash

# Puper API Development Server
# This script starts the development server with proper reload functionality

echo "🚽 Starting Puper API Development Server..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source .venv/bin/activate
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

# Start the development server
echo "🚀 Starting development server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
