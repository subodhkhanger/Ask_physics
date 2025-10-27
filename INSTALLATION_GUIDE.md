# Complete Installation & Testing Guide

## Full Setup Guide for Plasma Physics Literature Search

This guide will walk you through setting up the entire application from scratch, including Python virtual environment, OpenAI integration, and testing all components.

---

## Prerequisites

### Required Software

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **Node.js 18+** (for frontend)
   ```bash
   node --version  # Should be 18.0 or higher
   npm --version   # Should be 9.0 or higher
   ```

3. **Docker Desktop** (for Fuseki triple store)
   - Download from: https://www.docker.com/products/docker-desktop
   - Start Docker Desktop after installation

4. **Git** (should already be installed)
   ```bash
   git --version
   ```

5. **OpenAI API Key** (optional but recommended)
   - Get one from: https://platform.openai.com/api-keys
   - Keep it handy for configuration

---

## Step 1: Clone & Navigate to Project

```bash
# If not already in the project directory
cd /Users/ronnie/Documents/askPhysics

# Verify you're in the right place
ls -la
# You should see: backend/, frontend/, scripts/, data/, etc.
```

---

## Step 2: Python Virtual Environment Setup

### Create Virtual Environment

```bash
# Create virtual environment in the project root
python3 -m venv venv

# Expected output: A new 'venv' directory will be created
```

### Activate Virtual Environment

#### On macOS/Linux:
```bash
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
# Example: (venv) ronnie@MacBook askPhysics %
```

#### On Windows:
```bash
venv\Scripts\activate
```

### Verify Activation

```bash
which python
# Should show: /Users/ronnie/Documents/askPhysics/venv/bin/python

python --version
# Should show: Python 3.10.x or higher
```

---

## Step 3: Install Python Dependencies

### Install Main Requirements

```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
pip install --upgrade pip

# Install main dependencies
pip install -r requirements.txt

# This installs:
# - arxiv (for paper collection)
# - python-dotenv (for environment variables)
# - openai (for LLM-enhanced extraction)
```

### Install Backend API Dependencies

```bash
# Install backend-specific dependencies
pip install -r backend/requirements.txt

# This installs:
# - fastapi (web framework)
# - uvicorn (ASGI server)
# - pydantic (data validation)
# - SPARQLWrapper (SPARQL client)
# - requests, cachetools, pytest, etc.
```

### Verify Installation

```bash
# Check installed packages
pip list

# You should see packages like:
# arxiv, fastapi, uvicorn, openai, python-dotenv, pytest, etc.
```

---

## Step 4: Configure Environment Variables (OpenAI Key)

### Create .env File

```bash
# Copy the example environment file
cp .env.example .env

# Open .env for editing
nano .env
# Or use your preferred editor: code .env, vim .env, etc.
```

### Add Your OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```bash
# .env file content
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Example:
# OPENAI_API_KEY=sk-proj-abc123xyz789...
```

**Important**:
- Replace `sk-your-actual-openai-api-key-here` with your real key
- Keep this file private (it's already in .gitignore)
- Never commit this file to version control

### Verify .env File

```bash
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

---

## Step 5: Test Data Collection (Phase 1)

### Collect Sample Papers from arXiv

```bash
# Collect 5 papers for testing (without LLM)
python scripts/collect_papers.py --limit 5

# Expected output:
# Searching arXiv for plasma physics papers...
# Fetching up to 5 papers...
# Saved 5 papers to data/papers.json
# ✓ Successfully collected 5 papers
```

### Extract Parameters (Regex Only - No API Calls)

```bash
# Extract parameters using regex (free, no OpenAI needed)
python scripts/extract_parameters.py \
    --input data/sample_papers_with_params.json \
    --output data/extracted_test.json \
    --no-llm

# Expected output:
# Loading papers from data/sample_papers_with_params.json...
# Found 10 papers
# Extracting parameters (regex-only mode)...
# Extracted 24 temperature measurements
# Extracted 4 density measurements
# ✓ Successfully saved to data/extracted_test.json
```

### Test with OpenAI (Optional - Uses API Credits)

```bash
# Extract with LLM validation (requires OpenAI API key)
python scripts/extract_parameters.py \
    --input data/papers.json \
    --output data/extracted_with_llm.json

# Expected output:
# Loading papers from data/papers.json...
# Using OpenAI API for validation...
# Extracted X temperature measurements
# Extracted Y density measurements
# ✓ Successfully saved to data/extracted_with_llm.json
```

**Note**: This will use OpenAI API credits. Start with a small dataset!

### Verify Extracted Data

```bash
# View extracted parameters
cat data/extracted_test.json | head -50

# Or use jq for pretty printing (if installed)
cat data/extracted_test.json | jq '.[0]'
```

---

## Step 6: Build Knowledge Graph (Phase 2)

### Convert Data to RDF

```bash
# Convert extracted parameters to RDF triples
python scripts/convert_to_rdf.py \
    --input data/sample_extracted_params.json \
    --output data/plasma_data.ttl

# Expected output:
# Loading data from data/sample_extracted_params.json...
# Found 10 papers
# Converting to RDF triples...
# Writing 373 triples to data/plasma_data.ttl...
# ✓ Successfully created data/plasma_data.ttl
#   Papers: 10
#   Triples: ~373
#   Temperature measurements: 24
#   Density measurements: 4
```

### Start Fuseki Triple Store

```bash
# Make sure Docker Desktop is running!

# Start Fuseki and load data
bash scripts/setup_fuseki.sh

# Expected output:
# === Plasma Physics Knowledge Graph - Fuseki Setup ===
# Step 1: Starting Fuseki container...
# [+] Running 1/1
# ✔ Container plasma-fuseki  Started
#
# Step 2: Creating dataset 'plasma'...
# HTTP Status: 200
#
# Step 3: Loading ontology...
# HTTP Status: 200
#
# Step 4: Loading data...
# HTTP Status: 200
#
# === Setup Complete! ===
# Access Fuseki:
#   Web UI:         http://localhost:3030
#   Query endpoint: http://localhost:3030/plasma/query
#   Username:       admin
#   Password:       admin123
```

### Verify Fuseki is Running

```bash
# Check Fuseki web UI
curl http://localhost:3030

# Should return HTML content (Fuseki homepage)

# Test SPARQL endpoint
curl http://localhost:3030/plasma/query \
    --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
    -H "Accept: application/sparql-results+json" \
    -u admin:admin123

# Should return JSON with triple count (~373)
```

### Test SPARQL Queries

```bash
# Run Python SPARQL test script
python scripts/test_sparql.py

# Expected output:
# Testing connection to http://localhost:3030/plasma/query...
# ✓ Connection successful
#
# ============================================
# SPARQL Query Tests - Plasma Physics Knowledge Graph
# ============================================
#
# Query 1: Count total papers
# count
# 10
#
# Query 2: List papers with titles
# [Shows paper titles]
#
# Query 3: Temperature statistics (normalized to keV)
# count | avgKeV | maxKeV | minKeV
# 24    | 6.5    | 15.0   | 0.003
# ...
```

---

## Step 7: Start Backend API (Phase 3)

### Start FastAPI Server

Open a **new terminal** (keep Fuseki running in the first one):

```bash
# Navigate to project directory
cd /Users/ronnie/Documents/askPhysics

# Activate virtual environment
source venv/bin/activate

# Start backend API
cd backend
python run.py

# Expected output:
# ================================================================================
# Starting Plasma Physics Literature Search API v1.0.0
# ================================================================================
# Host: 0.0.0.0:8000
# Docs: http://0.0.0.0:8000/docs
# Fuseki: http://localhost:3030/plasma/query
# Reload: True
# ================================================================================
#
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Starting Plasma Physics Literature Search API v1.0.0
# INFO:     Fuseki endpoint: http://localhost:3030/plasma/query
# INFO:     ✓ Connected to Fuseki
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Test API Endpoints

Open a **third terminal**:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "ok",
#   "fuseki_connected": true,
#   "version": "1.0.0"
# }

# Get statistics
curl http://localhost:8000/statistics

# Expected output:
# {
#   "papers": 10,
#   "temperature": {
#     "count": 24,
#     "avg_kev": 6.5,
#     "max_kev": 15.0,
#     "min_kev": 0.003
#   },
#   "density": {
#     "count": 4,
#     "avg_density": 5.5e19,
#     "max_density": 8.9e19,
#     "min_density": 4.0e19
#   }
# }

# List papers
curl http://localhost:8000/papers

# Filter temperatures (> 10 keV)
curl "http://localhost:8000/temperatures?min_temp=10"

# Search papers
curl "http://localhost:8000/papers/search?q=tokamak"
```

### Access API Documentation

Open your browser:

```
http://localhost:8000/docs
```

You should see the **Swagger UI** with all 14 API endpoints. Try:
1. Click on `/health` endpoint
2. Click "Try it out"
3. Click "Execute"
4. See the response

---

## Step 8: Run Backend Tests

```bash
# Make sure you're in the backend directory with venv activated
cd /Users/ronnie/Documents/askPhysics/backend

# Run all tests
pytest -v

# Expected output:
# ===== test session starts =====
# backend/tests/test_api.py::test_health_check PASSED
# backend/tests/test_api.py::test_list_papers PASSED
# backend/tests/test_api.py::test_temperature_statistics PASSED
# ...
# ===== 25 passed in 2.45s =====

# Run with coverage
pytest --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Step 9: Start Frontend (Phase 4)

### Install Frontend Dependencies

Open a **fourth terminal**:

```bash
cd /Users/ronnie/Documents/askPhysics/frontend

# Install Node.js dependencies
npm install

# Expected output:
# added 234 packages in 15s
```

### Start Development Server

```bash
npm run dev

# Expected output:
#
#   VITE v5.0.11  ready in 523 ms
#
#   ➜  Local:   http://localhost:3000/
#   ➜  Network: use --host to expose
#   ➜  press h to show help
```

### Access Frontend

Open your browser:

```
http://localhost:3000
```

You should see the **Plasma Physics Literature Search** homepage with:
- System status indicator
- Statistics cards (Papers, Temperature, Density)
- Quick action buttons
- Feature descriptions

---

## Step 10: Full System Test

At this point, you should have **4 terminals running**:

1. **Terminal 1**: Fuseki (Docker)
2. **Terminal 2**: Backend API (FastAPI)
3. **Terminal 3**: Frontend (React/Vite)
4. **Terminal 4**: Free for commands

### Test Complete Workflow

1. **Open Frontend**: http://localhost:3000
2. **Check Status**: Green indicator = all systems operational
3. **View Statistics**: See 10 papers, 24 temperatures, 4 densities
4. **Browse Papers**: Click "Browse Papers" → See list of papers
5. **Filter Temperatures**: Click "Filter by Temperature"
6. **View API Docs**: http://localhost:8000/docs

### Test API Integration

```bash
# In Terminal 4
curl http://localhost:8000/health
curl http://localhost:8000/statistics
curl "http://localhost:8000/temperatures?min_temp=5&max_temp=15"
```

---

## Common Issues & Solutions

### Issue 1: Virtual Environment Not Activating

**Problem**: `source venv/bin/activate` doesn't work

**Solution**:
```bash
# Make sure you created it first
python3 -m venv venv

# Try full path
source /Users/ronnie/Documents/askPhysics/venv/bin/activate

# On Windows
venv\Scripts\activate.bat
```

### Issue 2: "Module not found" Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Make sure venv is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### Issue 3: Docker Not Running

**Problem**: `docker: command not found` or connection refused

**Solution**:
```bash
# Start Docker Desktop application
# Wait for it to fully start (whale icon in menu bar)

# Verify Docker is running
docker ps

# Restart Fuseki
docker compose down
bash scripts/setup_fuseki.sh
```

### Issue 4: Port Already in Use

**Problem**: `Address already in use` for port 8000

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
cd backend
python run.py --port 8001
```

### Issue 5: OpenAI API Key Not Working

**Problem**: `OpenAIError: Incorrect API key provided`

**Solution**:
```bash
# Check .env file exists
cat .env

# Verify key format (should start with sk-)
# OPENAI_API_KEY=sk-proj-...

# Test key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"

# Should print your key (starting with sk-)
```

### Issue 6: CORS Errors in Frontend

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:
```bash
# Backend should already have CORS enabled
# Check backend/config.py has:
# cors_origins: list = ["http://localhost:3000"]

# Restart backend
cd backend
python run.py
```

---

## Testing Checklist

Use this checklist to verify everything works:

### Backend Tests
- [ ] Virtual environment activated (`which python` shows venv)
- [ ] Dependencies installed (`pip list` shows fastapi, etc.)
- [ ] .env file created with OpenAI key
- [ ] Data collected (`ls data/papers.json`)
- [ ] Parameters extracted (`ls data/extracted_test.json`)
- [ ] RDF data generated (`ls data/plasma_data.ttl`)
- [ ] Fuseki running (`curl http://localhost:3030`)
- [ ] SPARQL queries work (`python scripts/test_sparql.py`)
- [ ] API running (`curl http://localhost:8000/health`)
- [ ] API tests pass (`cd backend && pytest`)
- [ ] Swagger UI accessible (http://localhost:8000/docs)

### Frontend Tests
- [ ] Node.js installed (`node --version`)
- [ ] Dependencies installed (`ls frontend/node_modules`)
- [ ] Dev server running (`npm run dev`)
- [ ] Homepage loads (http://localhost:3000)
- [ ] Statistics show correctly
- [ ] Navigation works
- [ ] API calls succeed (check browser console)

---

## Quick Start Commands Summary

```bash
# 1. Setup
cd /Users/ronnie/Documents/askPhysics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Generate Data
python scripts/extract_parameters.py \
    --input data/sample_papers_with_params.json \
    --output data/extracted_test.json \
    --no-llm

python scripts/convert_to_rdf.py \
    --input data/sample_extracted_params.json \
    --output data/plasma_data.ttl

# 3. Start Services (in separate terminals)
# Terminal 1: Fuseki
bash scripts/setup_fuseki.sh

# Terminal 2: Backend API (activate venv first!)
source venv/bin/activate
cd backend
python run.py

# Terminal 3: Frontend
cd frontend
npm install
npm run dev

# 4. Test
# Open http://localhost:3000
# Open http://localhost:8000/docs
```

---

## Stopping the Application

```bash
# Stop Frontend (Terminal 3)
Ctrl+C

# Stop Backend (Terminal 2)
Ctrl+C

# Stop Fuseki (Terminal 1)
Ctrl+C
# OR
docker compose down

# Deactivate virtual environment
deactivate
```

---

## Next Steps

Now that everything is running, you can:

1. **Explore the Data**:
   - Browse papers in the web UI
   - Filter by temperature ranges
   - View statistics and charts

2. **Add More Data**:
   ```bash
   python scripts/collect_papers.py --limit 50
   python scripts/extract_parameters.py --input data/papers.json
   python scripts/convert_to_rdf.py --input data/extracted_params.json --output data/new_data.ttl
   # Reload into Fuseki
   ```

3. **Customize**:
   - Modify frontend styles in `frontend/src/index.css`
   - Add new API endpoints in `backend/main.py`
   - Create custom SPARQL queries

4. **Deploy**:
   - See `backend/README.md` for deployment options
   - See `frontend/README.md` for static hosting

---

## Getting Help

- **Backend API**: http://localhost:8000/docs
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **Phase Docs**: `PHASE1_COMPLETE.md`, `PHASE2_COMPLETE.md`, `PHASE3_COMPLETE.md`
- **Quick Start**: `QUICK_START.md`

---

**Congratulations!** 🎉 You now have a fully functional plasma physics literature search system running locally!
