#!/bin/bash

# Horse Breed Service Startup Script
# This script activates the virtual environment and starts the FastAPI service

echo "🐎 Starting Horse Breed Service..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "horse-breed-service-env" ]; then
    echo "❌ Virtual environment 'horse-breed-service-env' not found!"
    echo "Please create the virtual environment first:"
    echo "python -m venv horse-breed-service-env"
    exit 1
fi

# Check if start_service.py exists
if [ ! -f "start_service.py" ]; then
    echo "❌ start_service.py not found!"
    echo "Please ensure you're in the correct directory."
    exit 1
fi

# Activate virtual environment and start service
echo "🔄 Activating virtual environment..."
source horse-breed-service-env/Scripts/activate

echo "🚀 Starting Horse Breed Service..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🏥 Health check will be available at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the service"
echo "=================================="

# Start the service
python start_service.py