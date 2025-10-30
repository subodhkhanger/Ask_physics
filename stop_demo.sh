#!/bin/bash

# Stop Demo Script
# Stops all services for the Plasma Physics Literature Search demo

echo "=========================================="
echo "Stopping all services..."
echo "=========================================="
echo ""

# Stop frontend (if running)
echo "Stopping frontend..."
pkill -f "vite" 2>/dev/null && echo "✓ Frontend stopped" || echo "  Frontend not running"

# Stop backend (if running)
echo "Stopping backend..."
pkill -f "uvicorn.*backend.main" 2>/dev/null && echo "✓ Backend stopped" || echo "  Backend not running"

# Stop Fuseki
echo "Stopping Fuseki..."
cd "$(dirname "$0")"
docker compose down
echo "✓ Fuseki stopped"

echo ""
echo "=========================================="
echo "✅ All services stopped"
echo "=========================================="
echo ""
echo "To start again: ./start_demo.sh"
