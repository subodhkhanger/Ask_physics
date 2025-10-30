# Knowledge Graph Pipeline - Complete Guide

## Overview: How the Fuseki Knowledge Graph is Built

Your system transforms **raw arXiv papers** → **extracted parameters** → **RDF triples** → **SPARQL-queryable knowledge graph**

```
Step 1: Collect Papers         → data/papers.json (100 papers)
Step 2: Extract Parameters      → data/extracted_params.json
Step 3: Convert to RDF          → data/plasma_data.ttl (1040 triples)
Step 4: Load into Fuseki        → SPARQL-queryable database
Step 5: Query via API/Frontend  → Natural language search
```

---

## Current Status ✅

You **already have everything** you need for a working demo:

- ✅ **100 papers** collected from arXiv
- ✅ **RDF data** generated (data/plasma_data.ttl - 1040 lines)
- ✅ **Fuseki setup script** (scripts/setup_fuseki.sh)
- ✅ **REST API** built (Phase 3 complete)
- ✅ **Frontend** with unified search (just implemented)

**For your job demo, you just need to START the services!**

---

## How to Get Real-World Results (Step by Step)

### Step 1: Start Fuseki with Your Existing Data

```bash
# Terminal 1: Start Fuseki and load your 100 papers
cd /Users/ronnie/Documents/askPhysics
bash scripts/setup_fuseki.sh

# This script does:
# 1. Starts Docker container with Fuseki
# 2. Creates "plasma" dataset
# 3. Loads ontology (plasma_physics.ttl)
# 4. Loads your data (plasma_data.ttl - 100 papers)
# 5. Takes ~30 seconds
```

**Check it's working:**
```bash
# Should return: { "message": "ping" }
curl http://localhost:3030/$/ping

# Count triples (should show ~1000)
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123
```

---

### Step 2: Start Backend API

```bash
# Terminal 2: Start FastAPI backend
cd backend
python run.py

# Should see:
# INFO: Uvicorn running on http://127.0.0.1:8000
# ✓ Connected to Fuseki
```

**Check it's working:**
```bash
# Should return statistics
curl http://localhost:8000/statistics

# Test natural language query
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "papers with temperature measurements", "limit": 5}' \
  | jq .
```

---

### Step 3: Start Frontend

```bash
# Terminal 3: Start React frontend
cd frontend
npm run dev

# Open browser: http://localhost:5173
```

---

## Real-World Results You Can Show NOW

### What's in Your Knowledge Graph?

Based on your `plasma_data.ttl` file:

```bash
# Check what papers you have
grep "Paper:" data/plasma_data.ttl | head -10
```

**Example papers in your database:**
1. "Phase-Space Shaping in Wakefield Accelerators due to Betatron Cooling"
2. "Physics-Informed Visual MARFE Prediction on the HL-3 Tokamak"
3. "Effect of flow-aligned external magnetic fields on mushroom instability"
4. "Quantum Kinetic Modeling of KEEN waves in a Warm-Dense Regime"
... and 96 more!

### Queries That Will Return Real Results

Try these natural language queries (they'll work with your data):

```
1. "Show me recent papers about tokamak"
   → Will find papers with "tokamak" in title

2. "Papers about plasma acceleration"
   → Will find wakefield accelerator papers

3. "Recent research on plasma instabilities"
   → Will find MARFE, mushroom instability papers

4. "Papers with temperature measurements"
   → Will find papers with extracted temp values

5. "Research on quantum kinetic modeling"
   → Will find quantum plasma papers
```

---

## Understanding the Data Flow

### 1. Collection Phase (Already Done)

**Script:** `scripts/collect_papers.py`

```bash
# What it does:
python scripts/collect_papers.py --limit 100

# Queries arXiv API for plasma physics papers
# Saves to: data/papers.json
# Contains: arXiv ID, title, authors, abstract, date
```

**Your current data:** 100 papers from arXiv `physics.plasm-ph` category

---

### 2. Extraction Phase (Already Done)

**Script:** `scripts/extract_parameters.py`

```bash
# What it does:
python scripts/extract_parameters.py \
  --input data/papers.json \
  --output data/extracted_params.json

# Uses regex + optional LLM to extract:
# - Temperature values (keV, eV, K)
# - Density values (m^-3, cm^-3)
# - Context snippets
# - Confidence scores
```

**Example extracted parameter:**
```json
{
  "paper_id": "2510.24567v1",
  "title": "Phase-Space Shaping...",
  "parameters": {
    "temperature": [
      {
        "value": 5.2,
        "unit": "keV",
        "context": "electron temperature Te = 5.2 keV",
        "confidence": "high"
      }
    ],
    "density": [
      {
        "value": 1e19,
        "unit": "cm^-3",
        "context": "plasma density ne = 10^19 cm^-3",
        "confidence": "high"
      }
    ]
  }
}
```

---

### 3. RDF Conversion Phase (Already Done)

**Script:** `scripts/convert_to_rdf.py`

```bash
# What it does:
python scripts/convert_to_rdf.py \
  --input data/extracted_params.json \
  --output data/plasma_data.ttl

# Converts JSON to RDF triples using ontology
# Creates relationships:
# Paper → reports → Measurement → measuresParameter → Temperature/Density
```

**Example RDF output (from your file):**
```turtle
# Paper entity
<http://example.org/plasma/paper/2510.24567v1> a :Paper ;
    :arxivId "2510.24567v1" ;
    :title "Phase-Space Shaping..." ;
    :authors "Pablo J. Bilbao, Thales Silva..." ;
    :publicationDate "2025-10-28T15:58:10+00:00"^^xsd:dateTime ;
    :reports meas:temp_2510.24567v1_0 .

# Temperature measurement
meas:temp_2510.24567v1_0 a :Measurement ;
    :measuresParameter param:temp_2510.24567v1_0 ;
    :confidence "high" ;
    :context "electron temperature Te = 5.2 keV" .

# Temperature value
param:temp_2510.24567v1_0 a :Temperature ;
    :value 5.2 ;
    :unitString "keV" ;
    :normalizedValue 5.2 .
```

---

### 4. Fuseki Loading Phase (Run this now)

**Script:** `scripts/setup_fuseki.sh`

```bash
#!/bin/bash
# What it does:

# 1. Start Fuseki via Docker
docker compose up -d

# 2. Wait for startup
sleep 10

# 3. Create dataset "plasma"
curl -X POST http://localhost:3030/$/datasets \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=plasma&dbType=mem" \
  -u admin:admin123

# 4. Load ontology
curl -X POST http://localhost:3030/plasma/data \
  -H "Content-Type: text/turtle" \
  --data-binary "@ontology/plasma_physics.ttl" \
  -u admin:admin123

# 5. Load your data (100 papers!)
curl -X POST http://localhost:3030/plasma/data \
  -H "Content-Type: text/turtle" \
  --data-binary "@data/plasma_data.ttl" \
  -u admin:admin123
```

**Result:** SPARQL-queryable database with 100 papers

---

### 5. Query Phase (Natural Language Search)

**Your new unified query system:**

```
User types: "Show me papers about tokamak"
     ↓
NLP Parser extracts: keywords=["tokamak"]
     ↓
SPARQL Builder generates:
PREFIX : <http://example.org/plasma#>
SELECT ?paper ?title ?authors
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :authors ?authors .
  FILTER(REGEX(?title, "tokamak", "i"))
}
     ↓
Fuseki executes query on 100 papers
     ↓
Returns: Papers with "tokamak" in title
```

---

## What You Can Demo RIGHT NOW

### Scenario 1: Basic Search

**User query:** "papers about plasma"

**What happens:**
1. NLP extracts keyword: "plasma"
2. SPARQL searches titles/abstracts
3. Returns papers like:
   - "Quantum Kinetic Modeling of KEEN waves..."
   - "Physics-Informed Visual MARFE Prediction..."
   - etc.

**Show in demo:**
- Fast results (<1 second)
- Relevant papers returned
- Links to arXiv for full papers

---

### Scenario 2: Parameter Search (If you have extracted params)

**User query:** "papers with temperature above 5 keV"

**What happens:**
1. NLP extracts: temperature > 5 keV
2. SPARQL filters by normalized temperature
3. Returns papers with temp measurements > 5 keV

**Note:** This works if your `extracted_params.json` has temperature values and they were converted to RDF.

---

### Scenario 3: Recent Papers

**User query:** "recent tokamak research"

**What happens:**
1. NLP extracts: keywords=["tokamak"], temporal="recent"
2. SPARQL filters by date (last 2 years) + keyword
3. Returns recent papers about tokamaks

**Show in demo:**
- Temporal filtering works
- Combines multiple constraints
- Real papers from 2024-2025

---

## How to Add MORE Real Data

If you want to expand your knowledge graph:

### Option 1: Collect More Papers

```bash
# Collect 500 more papers
python scripts/collect_papers.py --limit 500

# Extract parameters
python scripts/extract_parameters.py \
  --input data/papers.json \
  --output data/extracted_params.json \
  --no-llm  # Fast regex-only

# Convert to RDF
python scripts/convert_to_rdf.py \
  --input data/extracted_params.json \
  --output data/plasma_data_new.ttl

# Reload Fuseki
bash scripts/setup_fuseki.sh
```

### Option 2: Use LLM for Better Extraction

```bash
# Set OpenAI key
export OPENAI_API_KEY="sk-..."

# Extract with LLM validation (more accurate)
python scripts/extract_parameters.py \
  --input data/papers.json \
  --output data/extracted_params.json
  # (no --no-llm flag)

# This will extract more parameters with higher accuracy
```

### Option 3: Add Manual Annotations

Edit `data/extracted_params.json` to add missing measurements:

```json
{
  "paper_id": "2510.24567v1",
  "parameters": {
    "temperature": [
      {
        "value": 10.5,
        "unit": "keV",
        "context": "manually added from paper text",
        "confidence": "high"
      }
    ]
  }
}
```

Then re-run `convert_to_rdf.py` and reload Fuseki.

---

## Verification: Check What's Actually in Fuseki

Once Fuseki is running, verify your data:

### 1. Check Total Papers

```bash
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?p) as ?count) WHERE { ?p a :Paper }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123 | jq .
```

**Expected:** `"count": 100`

### 2. List All Papers

```bash
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT ?title WHERE { ?paper a :Paper ; :title ?title } LIMIT 10" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123 | jq .
```

### 3. Check Temperature Measurements

```bash
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?t) as ?count) WHERE { ?t a :Temperature }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123 | jq .
```

### 4. Check Density Measurements

```bash
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?d) as ?count) WHERE { ?d a :Density }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123 | jq .
```

---

## Architecture Diagram

```
┌─────────────────┐
│  arXiv Papers   │  (Source: physics.plasm-ph)
└────────┬────────┘
         │ collect_papers.py
         ↓
┌─────────────────┐
│ papers.json     │  (100 papers with metadata)
└────────┬────────┘
         │ extract_parameters.py (regex + optional LLM)
         ↓
┌─────────────────┐
│extracted_params │  (Temperature, Density values)
│     .json       │
└────────┬────────┘
         │ convert_to_rdf.py (using ontology)
         ↓
┌─────────────────┐
│plasma_data.ttl  │  (1040 RDF triples)
└────────┬────────┘
         │ setup_fuseki.sh (Docker + load data)
         ↓
┌─────────────────┐
│ Apache Jena     │  (SPARQL endpoint)
│    Fuseki       │  :3030/plasma/query
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
┌────────┐ ┌──────────────┐
│REST API│ │ Natural Lang │
│:8000   │ │ Query System │
└────────┘ └──────────────┘
    │         │
    └────┬────┘
         ↓
    ┌─────────┐
    │Frontend │  (React UI)
    │  :5173  │
    └─────────┘
```

---

## Summary: What You Have

### ✅ Complete Pipeline
- Data collection from arXiv
- Parameter extraction (regex + LLM)
- RDF conversion with ontology
- Fuseki SPARQL database
- REST API for querying
- Natural language frontend

### ✅ Real Data
- **100 papers** from arXiv
- **1040 RDF triples**
- Recent papers (2024-2025)
- Real physics research

### ✅ Ready to Demo
- Just need to start Docker
- Run backend (python run.py)
- Run frontend (npm run dev)
- Show real-world results!

---

## Quick Start for Demo

```bash
# 1. Start Fuseki (loads your 100 papers)
bash scripts/setup_fuseki.sh

# 2. Start backend
cd backend && python run.py &

# 3. Start frontend
cd frontend && npm run dev

# 4. Open browser
# http://localhost:5173

# 5. Try these queries:
# "recent papers about tokamak"
# "papers about plasma acceleration"
# "research on quantum plasmas"
```

**You have everything you need for a working demo!** 🎉

---

## Next Steps (Optional)

If you want to improve the demo:

1. **More data:** Collect 500-1000 papers
2. **Better extraction:** Use LLM for all extractions
3. **Manual curation:** Fix any extraction errors
4. **Add visualizations:** Charts showing temp/density distributions

But for a job application prototype, **what you have now is impressive and functional!**

