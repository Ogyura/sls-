#!/bin/bash

# Start the Regional Analytics Backend Server

echo "Starting Regional Analytics API..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "Starting server on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
