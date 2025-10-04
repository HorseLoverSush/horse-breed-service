@echo off
:: Horse Breed Service Startup Script (Windows Batch)
:: This script activates the virtual environment and starts the FastAPI service

echo 🐎 Starting Horse Breed Service...
echo ==================================

:: Check if virtual environment exists
if not exist "horse-breed-service-env" (
    echo ❌ Virtual environment 'horse-breed-service-env' not found!
    echo Please create the virtual environment first:
    echo python -m venv horse-breed-service-env
    pause
    exit /b 1
)

:: Check if start_service.py exists
if not exist "start_service.py" (
    echo ❌ start_service.py not found!
    echo Please ensure you're in the correct directory.
    pause
    exit /b 1
)

:: Activate virtual environment and start service
echo 🔄 Activating virtual environment...
call horse-breed-service-env\Scripts\activate.bat

echo 🚀 Starting Horse Breed Service...
echo 📖 API Documentation will be available at: http://localhost:8000/docs
echo 🏥 Health check will be available at: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the service
echo ==================================

:: Start the service
python start_service.py

pause