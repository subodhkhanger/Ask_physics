# Clean Data and Rebuild Everything

This guide explains how to clean your data and rebuild the entire askPhysics pipeline from scratch.

## Quick Start

### Option 1: Automated Script (Recommended)

```bash
# Clean and rebuild everything (including collecting new papers)
./scripts/reset_and_rebuild.sh

# Or keep existing papers and just re-extract parameters
./scripts/reset_and_rebuild.sh --skip-collect
```

### Option 2: Manual Step-by-Step

Follow the steps below for more control over the process.

---

## Manual Step-by-Step Process

### 1. Backup Current Data (Optional)

```bash
# Create backup directory
mkdir -p data/backups/$(date +%Y%m%d_%H%M%S)

# Backup existing files
cp data/papers.json data/backups/$(date +%Y%m%d_%H%M%S)/
cp data/extracted_with_llm.json data/backups/$(date +%Y%m%d_%H%M%S)/
cp data/plasma_data.ttl data/backups/$(date +%Y%m%d_%H%M%S)/
```

### 2. Clean Existing Data

```bash
# Remove processed data files (keep papers.json if you want to reuse it)
rm -f data/extracted_with_llm.json
rm -f data/plasma_data.ttl

# Optional: Remove papers.json to collect fresh papers
# rm -f data/papers.json
```

### 3. Collect Papers from arXiv (if needed)

If you deleted `papers.json` or want fresh papers:

```bash
# Collect 300 papers (adjust --limit as needed)
python3 scripts/collect_papers_with_params.py \
    --limit 300 \
    --output data/papers.json
```

**Note**: This will take several minutes depending on the limit.

### 4. Deduplicate Papers

```bash
# Preview deduplication (dry run)
python3 scripts/deduplicate_data.py --dry-run

# Apply deduplication
python3 scripts/deduplicate_data.py
```

### 5. Extract Parameters

**With LLM (Recommended - more accurate):**

```bash
# Make sure OPENAI_API_KEY is set in .env file
python3 scripts/extract_parameters.py \
    --input data/papers.json \
    --output data/extracted_with_llm.json
```

**Without LLM (Faster but less accurate):**

```bash
python3 scripts/extract_parameters.py \
    --input data/papers.json \
    --output data/extracted_with_llm.json \
    --no-llm
```

### 6. Build Knowledge Graph

```bash
# Check if you have a KG builder script
ls scripts/build_knowledge_graph.py || ls scripts/build_kg.py

# Run the appropriate one
python3 scripts/build_knowledge_graph.py \
    --input data/extracted_with_llm.json \
    --output data/plasma_data.ttl
```

If you don't have a KG builder, the reset script will create a basic one.

### 7. Load Data into Fuseki

**Option A: Using Docker Compose**

```bash
# Stop Fuseki
docker-compose stop fuseki

# Remove old database
rm -rf fuseki-data/databases/plasma/*

# Start Fuseki (will reload data automatically if configured)
docker-compose up -d fuseki
```

**Option B: Manual Upload via Web Interface**

1. Open http://localhost:3030
2. Go to "manage datasets"
3. Select your dataset (usually "plasma")
4. Click "upload data"
5. Upload `data/plasma_data.ttl`

**Option C: Using SPARQL Update**

```bash
# Upload via HTTP
curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @data/plasma_data.ttl \
  http://localhost:3030/plasma/data
```

### 8. Restart Backend Server

```bash
# If running in development
cd backend
python run.py

# If using Docker
docker-compose restart backend

# If using systemd/process manager
sudo systemctl restart askphysics-backend
```

### 9. Verify Everything Works

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"ok","fuseki_connected":true,"version":"1.0.0"}

# Test statistics
curl http://localhost:8000/statistics

# Test natural language query
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me papers with temperature above 10 keV", "limit": 5}'
```

---

## Troubleshooting

### Papers Collection Fails

**Problem**: `ArxivAPIError` or connection timeout

**Solution**:
- Check internet connection
- Reduce `--limit` to smaller number
- Add delays between requests (already implemented in scripts)

### Parameter Extraction is Slow

**Problem**: Taking too long with LLM

**Solution**:
- Use `--no-llm` flag for faster (but less accurate) extraction
- Process fewer papers initially
- Check OpenAI API rate limits

### No Parameters Found

**Problem**: `extracted_with_llm.json` has all empty parameters

**Solution**:
- Check if papers actually contain measurements
- Try collecting different papers with better filtering
- Verify regex patterns in `extract_parameters.py`

### Fuseki Connection Fails

**Problem**: Backend can't connect to Fuseki

**Solution**:
```bash
# Check if Fuseki is running
curl http://localhost:3030/$/ping

# Check Docker logs
docker-compose logs fuseki

# Restart Fuseki
docker-compose restart fuseki
```

### Duplicate Entries Still Showing

**Problem**: After all fixes, still seeing duplicates

**Solution**:
1. Clear browser cache
2. Restart backend server
3. Check that updated `main.py` is being used
4. Verify deduplication logic was applied:
   ```bash
   grep -A 10 "Deduplicate papers by arxiv_id" backend/main.py
   ```

---

## Quick Reference Commands

```bash
# Full rebuild (automated)
./scripts/reset_and_rebuild.sh

# Rebuild keeping existing papers
./scripts/reset_and_rebuild.sh --skip-collect

# Rebuild with only 50 papers
./scripts/reset_and_rebuild.sh --limit 50

# Just deduplicate existing data
python3 scripts/deduplicate_data.py

# Check statistics
python3 -c "
import json
data = json.load(open('data/extracted_with_llm.json'))
papers_with_params = [d for d in data if d['parameters']['temperature'] or d['parameters']['density']]
print(f'Papers with parameters: {len(papers_with_params)}/{len(data)}')
print(f'Total temps: {sum(len(d[\"parameters\"][\"temperature\"]) for d in data)}')
print(f'Total densities: {sum(len(d[\"parameters\"][\"density\"]) for d in data)}')
"
```

---

## File Structure After Rebuild

```
askPhysics/
├── data/
│   ├── papers.json                  # Collected papers from arXiv
│   ├── extracted_with_llm.json      # Extracted parameters
│   ├── plasma_data.ttl              # RDF knowledge graph
│   └── backups/                     # Timestamped backups
│       └── 20251030_120000/
│           ├── papers.json
│           ├── extracted_with_llm.json
│           └── plasma_data.ttl
├── fuseki-data/
│   └── databases/
│       └── plasma/                  # Fuseki database files
└── backend/
    └── main.py                      # Updated with deduplication
```

---

## What Gets Fixed

After running the cleanup and rebuild:

✓ **Duplicate paper entries removed**
✓ **Duplicate parameters within papers removed**
✓ **API responses deduplicated**
✓ **Fresh knowledge graph generated**
✓ **Clean database state**

The deduplication happens at multiple levels:
1. **Source data**: `deduplicate_data.py` removes duplicates from JSON files
2. **API layer**: `main.py` deduplicates results before returning to frontend
3. **Query layer**: SPARQL uses `SELECT DISTINCT` to avoid duplicates at query time
