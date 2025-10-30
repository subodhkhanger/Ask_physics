# ✅ Fixed Startup Guide

The backend import issues have been **fixed**! Here's how to start everything:

---

## Method 1: Manual (Recommended - Most Reliable)

### Terminal 1 - Fuseki
```bash
cd /Users/ronnie/Documents/askPhysics
bash scripts/setup_fuseki.sh
```
**Wait for:** "Server started on port 3030"

### Terminal 2 - Backend
```bash
cd /Users/ronnie/Documents/askPhysics
source venv/bin/activate
cd backend
python3 run.py
```
**Wait for:** "Uvicorn running on http://0.0.0.0:8000"

### Terminal 3 - Frontend
```bash
cd /Users/ronnie/Documents/askPhysics/frontend
npm run dev
```
**Wait for:** "Local: http://localhost:5173"

### Open Browser
http://localhost:5173

---

## Method 2: Automated Script

```bash
cd /Users/ronnie/Documents/askPhysics
./start_demo.sh
```

**Note:** The script should now work correctly after the fixes!

---

## What Was Fixed

1. ✅ **Import errors** - Fixed relative imports in `main.py`, `sparql_client.py`, `cache.py`, `query_builder.py`
2. ✅ **Missing BaseModel import** - Added to `main.py`
3. ✅ **Virtual environment handling** - Script now activates venv properly

---

## Quick Test (Without Frontend)

Once Fuseki and Backend are running:

```bash
# Test basic health
curl http://localhost:8000/health

# Test natural language query
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers about tokamak", "limit": 5}' \
  | python3 -m json.tool
```

---

## Demo Queries to Try

1. **"recent papers about tokamak"**
2. **"papers about plasma acceleration"**
3. **"research on quantum plasmas"**
4. **"papers on magnetic fields in plasmas"**
5. **"plasma instability studies"**

All of these will return **real results** from your 100-paper knowledge graph!

---

## Stop Everything

```bash
# Stop frontend: Ctrl+C in Terminal 3
# Stop backend: Ctrl+C in Terminal 2
# Stop Fuseki:
docker compose down
```

Or use the stop script:
```bash
./stop_demo.sh
```

---

## Troubleshooting

### "No module named 'fastapi'"
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

### "Docker daemon not running"
Start Docker Desktop application first

### "OpenAI API key warning"
This is OK! System falls back to regex-only mode.
To add key (optional):
```bash
export OPENAI_API_KEY="sk-your-key"
```

---

## You're Ready! 🎉

Everything is fixed and ready for your demo. Just run the 3 commands above and you'll have a working natural language search system for plasma physics literature!
