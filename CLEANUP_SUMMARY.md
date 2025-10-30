# Data Cleanup and Rebuild - Summary Report

**Date**: October 30, 2025
**Status**: ✓ Complete

---

## What Was Done

### 1. Fixed Duplicate Entry Issue

**Problem**: Same paper appearing multiple times in query results

**Root Cause**: When papers have multiple measurements (e.g., 3 temperature values), SPARQL returns 3 rows - one per measurement. The API was not deduplicating these before sending to the frontend.

**Solution Applied**:
- Updated `backend/main.py` to deduplicate papers by `arxiv_id` in three endpoints:
  - `/query/natural-language` (line 557-573)
  - `/papers` (line 139-154)
  - `/papers/search` (line 232-244)

### 2. Created Data Management Tools

**New Scripts Created**:

1. **`scripts/deduplicate_data.py`** - Deduplicates papers and parameters
   ```bash
   python3 scripts/deduplicate_data.py --dry-run  # preview
   python3 scripts/deduplicate_data.py            # apply
   ```

2. **`scripts/build_knowledge_graph.py`** - Builds RDF/TTL from extracted data
   ```bash
   python3 scripts/build_knowledge_graph.py \
     --input data/extracted_with_llm.json \
     --output data/plasma_data.ttl
   ```

3. **`scripts/reset_and_rebuild.sh`** - One-command full pipeline rebuild
   ```bash
   ./scripts/reset_and_rebuild.sh
   ```

### 3. Cleaned and Rebuilt Data

**Data Verification Results**:
```
Total papers collected: 300
Papers with parameters: 18
Papers without parameters: 282

Temperature measurements: 30
Density measurements: 0

Unique paper IDs: 300
Duplicate IDs: 0 ✓
```

**Knowledge Graph Stats**:
```
Papers in KG: 18
Measurements: 30
Parameters: 30
File size: 20.6 KB
Generated: 2025-10-30T18:20:29
```

---

## Current Data State

### Files Updated

| File | Status | Size | Notes |
|------|--------|------|-------|
| `data/papers.json` | ✓ Clean | 507 KB | 300 unique papers |
| `data/extracted_with_llm.json` | ✓ Clean | - | 18 papers with params |
| `data/plasma_data.ttl` | ✓ Rebuilt | 20.6 KB | Fresh from real data |
| `backend/main.py` | ✓ Updated | - | Deduplication added |

### Backups Created

All backups saved in `data/backups/20251030_181918/`:
- `papers_backup_20251030_181918.json`
- `extracted_with_llm_backup_20251030_181918.json`
- `plasma_data_backup_20251030_181918.ttl`

---

## Next Steps - Action Required

### 1. Reload Data into Fuseki

The TTL file has been regenerated with real data. You need to reload it:

**Option A: Docker Compose (Recommended)**
```bash
# Stop Fuseki
docker-compose stop fuseki

# Clear old database
rm -rf fuseki-data/databases/plasma/*

# Restart Fuseki (will reload from data/plasma_data.ttl)
docker-compose up -d fuseki
```

**Option B: Web Interface**
1. Visit http://localhost:3030
2. Go to "manage datasets" → "plasma"
3. Click "upload data"
4. Upload `data/plasma_data.ttl`

**Option C: Command Line**
```bash
curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @data/plasma_data.ttl \
  http://localhost:3030/plasma/data
```

### 2. Restart Backend Server

The updated `main.py` needs to be loaded:

```bash
# If running manually
cd backend
python run.py

# If using Docker
docker-compose restart backend

# If using process manager
sudo systemctl restart askphysics-backend
```

### 3. Verify Everything Works

```bash
# Test health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","fuseki_connected":true,"version":"1.0.0"}

# Test query (should have NO duplicates now)
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me papers with temperature measurements",
    "limit": 10,
    "include_sparql": true
  }'
```

### 4. Test in Browser

1. Open your frontend application
2. Search for papers with parameters
3. Verify **no duplicate entries** appear
4. Each paper should appear only once, even if it has multiple measurements

---

## Files Reference

### Documentation
- **[CLEANUP_AND_REBUILD.md](CLEANUP_AND_REBUILD.md)** - Complete rebuild guide
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - This file

### Scripts
- **[scripts/deduplicate_data.py](scripts/deduplicate_data.py)** - Deduplication tool
- **[scripts/build_knowledge_graph.py](scripts/build_knowledge_graph.py)** - KG builder
- **[scripts/reset_and_rebuild.sh](scripts/reset_and_rebuild.sh)** - Automated rebuild

### Updated Code
- **[backend/main.py](backend/main.py)** - API with deduplication (lines 139-154, 232-244, 557-573)

---

## Quick Commands Reference

```bash
# Full rebuild from scratch
./scripts/reset_and_rebuild.sh

# Just deduplicate existing data
python3 scripts/deduplicate_data.py

# Rebuild knowledge graph
python3 scripts/build_knowledge_graph.py

# Check data stats
python3 -c "
import json
data = json.load(open('data/extracted_with_llm.json'))
print(f'Papers with params: {len([d for d in data if d[\"parameters\"][\"temperature\"] or d[\"parameters\"][\"density\"]])}/{len(data)}')
"

# Reload Fuseki + restart backend
docker-compose restart fuseki backend

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/statistics
```

---

## Summary

✓ **Duplicate issue fixed** - API now deduplicates results
✓ **Data verified clean** - No duplicate papers in source data
✓ **Knowledge graph rebuilt** - Fresh TTL from real extracted data
✓ **Tools created** - Scripts for future data management
✓ **Backups made** - Original data preserved

**Action Required**: Reload Fuseki database and restart backend to apply changes.

---

## Questions or Issues?

If you encounter any problems:

1. Check [CLEANUP_AND_REBUILD.md](CLEANUP_AND_REBUILD.md) troubleshooting section
2. Verify Fuseki is running: `curl http://localhost:3030/$/ping`
3. Check backend logs for errors
4. Ensure updated `main.py` is being used
