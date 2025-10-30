#!/bin/bash

# Simple Backend Startup Script
# Starts the FastAPI backend using the virtual environment

cd "$(dirname "$0")/backend"

# Activate virtual environment and run
source ../venv/bin/activate

echo "Starting Backend API..."
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

python3 run.py
