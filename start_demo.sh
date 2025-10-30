#!/bin/bash

# Quick Demo Startup Script
# Starts all services for the Plasma Physics Literature Search demo

set -e  # Exit on any error

echo "=========================================="
echo "Starting Plasma Physics Literature Search"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ] && grep -q "OPENAI_API_KEY" .env; then
        echo "✓ OpenAI API key found in .env file"
    else
        echo "⚠️  Warning: OPENAI_API_KEY not set"
        echo "   Natural language queries may fall back to regex-only mode."
        echo "   To enable LLM:"
        echo "   export OPENAI_API_KEY='sk-your-key'"
        echo ""
        read -p "Continue without LLM? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "Step 1/3: Starting Fuseki (Knowledge Graph)..."
echo "----------------------------------------------"
bash scripts/setup_fuseki.sh

# Wait for Fuseki to be ready
echo "Waiting for Fuseki to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3030/$/ping > /dev/null 2>&1; then
        echo "✓ Fuseki is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Fuseki failed to start within 30 seconds"
        echo "   Check Docker logs: docker compose logs"
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Count papers loaded
PAPER_COUNT=$(curl -s -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?p) as ?count) WHERE { ?p a :Paper }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123 2>/dev/null | grep -o '"value":"[0-9]*"' | grep -o '[0-9]*' || echo "0")

echo "✓ Knowledge graph loaded with $PAPER_COUNT papers"
echo ""

echo "Step 2/3: Starting Backend API..."
echo "----------------------------------------------"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Check if requirements are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
fi

# Start backend in background
cd backend
python3 run.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend API is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Backend failed to start within 20 seconds"
        echo "   Check logs: tail backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

echo "Step 3/3: Starting Frontend..."
echo "----------------------------------------------"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install
fi

echo "✓ Frontend starting..."
echo ""

# Start frontend (this will stay in foreground)
echo "=========================================="
echo "✅ All services started successfully!"
echo "=========================================="
echo ""
echo "🌐 Open your browser to: http://localhost:5173"
echo ""
echo "📊 Available endpoints:"
echo "   - Frontend:  http://localhost:5173"
echo "   - Backend API: http://localhost:8000/docs"
echo "   - Fuseki UI:   http://localhost:3030 (admin/admin123)"
echo ""
echo "🔍 Try these example queries:"
echo "   1. 'recent papers about tokamak'"
echo "   2. 'papers about plasma acceleration'"
echo "   3. 'research on quantum plasmas'"
echo ""
echo "⏹️  To stop all services:"
echo "   - Press Ctrl+C to stop frontend"
echo "   - Run: ./stop_demo.sh"
echo ""
echo "Starting frontend now..."
echo "=========================================="
echo ""

npm run dev

# This will only be reached if user stops frontend with Ctrl+C
echo ""
echo "Frontend stopped. Backend and Fuseki are still running."
echo "To stop all services: ./stop_demo.sh"
