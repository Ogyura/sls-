# Regional Analytics Backend Startup Script for Windows

Write-Host "Starting Regional Analytics API..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# Start the server
Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
