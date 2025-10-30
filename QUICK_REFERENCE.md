# askPhysics Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Start services
docker-compose up -d

# 2. Check health
curl http://localhost:8000/health

# 3. Test query
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "Papers with temperature above 1 keV", "limit": 5}'
```

---

## 📊 Current Database Status

| Metric | Value |
|--------|-------|
| Total Papers | 300 |
| Papers with Parameters | 18 |
| **Temperature Measurements** | **30** ✓ |
| **Density Measurements** | **0** ✗ |
| Temperature Range | 0.0 - 30.0 keV |

---

## 🔍 What You Can Search For

### ✓ Working Queries (Have Data)

**Temperature queries:**
- "Papers with temperature measurements"
- "Temperature above 1 keV"
- "High temperature experiments above 5 keV"
- "Temperature between 0.1 and 10 keV"

### ✗ Not Working Yet (No Data)

**Density queries:**
- "Papers with density measurements" → Returns 0 results
- "Density above 10^19 m^-3" → Returns 0 results

**Why?** No density measurements in database yet.

---

## 🔧 Common Commands

### Data Management

```bash
# Full rebuild
./scripts/reset_and_rebuild.sh

# Just deduplicate
python3 scripts/deduplicate_data.py

# Rebuild knowledge graph
python3 scripts/build_knowledge_graph.py

# Check what you have
python3 -c "
import json
data = json.load(open('data/extracted_with_llm.json'))
temps = sum(len(d['parameters']['temperature']) for d in data)
dens = sum(len(d['parameters']['density']) for d in data)
print(f'Temps: {temps}, Densities: {dens}')
"
```

### Query Examples

```bash
# Get statistics
curl http://localhost:8000/statistics

# List all temperatures
curl http://localhost:8000/temperatures

# Temperature range
curl "http://localhost:8000/temperatures?min_temp=1.0&max_temp=10.0"

# Natural language
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "YOUR QUERY HERE", "limit": 10}'
```

### Service Management

```bash
# Start everything
docker-compose up -d

# Restart services
docker-compose restart fuseki backend

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f fuseki
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No results found" for density | Normal - no density data yet |
| Duplicate papers showing | Restart backend: `docker-compose restart backend` |
| Fuseki not connecting | `curl http://localhost:3030/$/ping` |
| API not responding | Check logs: `docker-compose logs backend` |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `data/papers.json` | 300 collected papers |
| `data/extracted_with_llm.json` | Extracted parameters |
| `data/plasma_data.ttl` | RDF knowledge graph |
| `backend/main.py` | API with deduplication |
| `scripts/build_knowledge_graph.py` | Build KG from JSON |

---

## 📚 Documentation

- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - What was fixed
- **[CLEANUP_AND_REBUILD.md](CLEANUP_AND_REBUILD.md)** - Full rebuild guide
- **[QUERY_EXAMPLES.md](QUERY_EXAMPLES.md)** - All query examples
- **[HOW_SEARCH_WORKS.md](HOW_SEARCH_WORKS.md)** - Search flow explained

---

## 🎯 Next Actions

After restart, you should:

1. **Reload Fuseki database:**
   ```bash
   docker-compose restart fuseki
   ```

2. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

3. **Test it works:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/statistics
   ```

4. **Verify no duplicates:**
   - Open frontend
   - Search for papers with temperature
   - Each paper should appear only once ✓

---

## 💡 Tips

- Use `include_sparql: true` to debug queries
- Check `/docs` for interactive API documentation
- Temperature units auto-normalize to keV
- Density units would normalize to m^-3 (when you have data)
- SPARQL endpoint: http://localhost:3030/plasma/query

---

## 🚨 Known Limitations

1. **No density data** - Papers don't have density or extraction failed
2. **Only 18 papers** have parameters out of 300 (6%)
3. **Temperature only** - Can't query density yet

To improve:
- Collect more papers with measurements
- Improve extraction patterns
- Use LLM extraction (set OPENAI_API_KEY)
