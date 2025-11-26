#!/bin/bash

# Start script for Banking REST API Service
# Activates virtual environment and starts the FastAPI server

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
echo "Starting Banking REST API Service..."
echo "Server will be available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

