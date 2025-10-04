# Horse Breed Service Startup Script (PowerShell)
# This script activates the virtual environment and starts the FastAPI service

Write-Host "🐎 Starting Horse Breed Service..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "horse-breed-service-env")) {
    Write-Host "❌ Virtual environment 'horse-breed-service-env' not found!" -ForegroundColor Red
    Write-Host "Please create the virtual environment first:" -ForegroundColor Yellow
    Write-Host "python -m venv horse-breed-service-env" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if start_service.py exists
if (-not (Test-Path "start_service.py")) {
    Write-Host "❌ start_service.py not found!" -ForegroundColor Red
    Write-Host "Please ensure you're in the correct directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and start service
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "horse-breed-service-env\Scripts\Activate.ps1"

Write-Host "🚀 Starting Horse Breed Service..." -ForegroundColor Green
Write-Host "📖 API Documentation will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏥 Health check will be available at: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Green

# Start the service
python start_service.py