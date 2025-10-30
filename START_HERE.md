# Quick Start - Manual Method (Most Reliable)

If `start_demo.sh` is having issues, use this **manual 3-terminal method**:

---

## Terminal 1: Start Fuseki (Knowledge Graph)

```bash
cd /Users/ronnie/Documents/askPhysics
bash scripts/setup_fuseki.sh
```

**Wait for:** "Server started on port 3030"

**Test it works:**
```bash
curl http://localhost:3030/$/ping
# Should return: {"message":"ping"}
```

---

## Terminal 2: Start Backend API

```bash
cd /Users/ronnie/Documents/askPhysics

# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
python3 run.py
```

**Wait for:** "Uvicorn running on http://0.0.0.0:8000"

**Test it works:**
```bash
# In another terminal:
curl http://localhost:8000/health
# Should return: {"status":"ok",...}
```

---

## Terminal 3: Start Frontend

```bash
cd /Users/ronnie/Documents/askPhysics/frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm run dev
```

**Wait for:** "Local: http://localhost:5173"

---

## Open Browser

Navigate to: **http://localhost:5173**

---

## Try These Queries

1. **"recent papers about tokamak"**
2. **"papers about plasma acceleration"**
3. **"research on quantum plasmas"**
4. **"papers on magnetic fields"**

---

## Troubleshooting

### Backend won't start - Import Error

If you see `ModuleNotFoundError: No module named 'fastapi'`:

```bash
cd /Users/ronnie/Documents/askPhysics
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Backend won't start - OpenAI Warning

If you see "No OpenAI API key found":

```bash
# This is OK! The system will fall back to regex-only mode
# Queries will still work, just without LLM parsing

# To add OpenAI (optional):
export OPENAI_API_KEY="sk-your-key-here"
```

### Fuseki won't start

```bash
# Check Docker is running
docker ps

# If Docker daemon not running, start Docker Desktop app first
```

### Frontend build errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Stop Everything

**Terminal 1 (Fuseki):** Press `Ctrl+C`, then:
```bash
docker compose down
```

**Terminal 2 (Backend):** Press `Ctrl+C`

**Terminal 3 (Frontend):** Press `Ctrl+C`

---

## Quick Test Without Frontend

Once Fuseki and Backend are running, test the natural language query API:

```bash
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "papers about tokamak",
    "limit": 5,
    "include_sparql": true
  }' | python3 -m json.tool
```

Should return papers with "tokamak" in the title!

---

## Summary

**3 terminals, 3 commands:**

1. `bash scripts/setup_fuseki.sh`
2. `source venv/bin/activate && cd backend && python3 run.py`
3. `cd frontend && npm run dev`

**Then open:** http://localhost:5173

That's it! 🎉
