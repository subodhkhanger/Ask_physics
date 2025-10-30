# How Search Works in askPhysics

This document explains what happens when you search for density or temperature parameters.

---

## Your Current Data

**Total Papers**: 300
**Papers with Parameters**: 18

### Available Measurements:
- ✓ **Temperature**: 30 measurements across 18 papers
- ✗ **Density**: 0 measurements (none extracted yet)

### Why No Density?

The current papers either:
1. Don't contain density measurements
2. Have density in formats the extractor doesn't recognize

---

## Query Flow Diagram

```
User Query: "Show papers with density above 10^19 m^-3"
     ↓
┌────────────────────────────────────────┐
│ 1. NLP Query Processor                 │
│    - Parses natural language           │
│    - Extracts: parameter type (density)│
│    - Extracts: range (min: 1e19 m^-3)  │
│    - Extracts: keywords, dates, etc.   │
└─────────────────┬──────────────────────┘
                  ↓
┌────────────────────────────────────────┐
│ 2. SPARQL Query Builder                │
│    - Converts parsed params to SPARQL  │
│    - Adds filters for density range    │
│    - Adds DISTINCT to avoid duplicates │
└─────────────────┬──────────────────────┘
                  ↓
         Generated SPARQL:

         PREFIX : <http://example.org/plasma#>
         SELECT DISTINCT ?paper ?title ?authors
         WHERE {
           ?paper a :Paper ;
                  :title ?title ;
                  :reports ?densMeas .
           ?densMeas :measuresParameter ?dens .
           ?dens a :Density ;
                 :normalizedValue ?densValue .
           FILTER(?densValue >= 1e19)
         }
         LIMIT 20
                  ↓
┌────────────────────────────────────────┐
│ 3. Fuseki SPARQL Endpoint              │
│    - Executes query on RDF database    │
│    - Returns matching triples          │
└─────────────────┬──────────────────────┘
                  ↓
          Results from Fuseki:
          (If density data exists)

          {
            "paper": "http://.../paper/123",
            "title": "High density plasma...",
            "authors": "Smith et al."
          }
                  ↓
┌────────────────────────────────────────┐
│ 4. API Response Handler (main.py)     │
│    - Formats SPARQL results            │
│    - DEDUPLICATES papers by arxiv_id   │ ← FIX APPLIED!
│    - Converts to JSON                  │
└─────────────────┬──────────────────────┘
                  ↓
          Final JSON Response:

          {
            "parsed_query": {...},
            "papers": [
              {
                "arxiv_id": "123",
                "title": "High density plasma...",
                "authors": "Smith et al."
              }
            ],
            "total_results": 1,
            "execution_time_ms": 45.2
          }
                  ↓
┌────────────────────────────────────────┐
│ 5. Frontend Display                    │
│    - Shows unique papers (no duplicates)│
│    - Each paper appears only once      │
└────────────────────────────────────────┘
```

---

## What Happens With Current Data

### Density Query Example

**Query**: "Show papers with density above 10^19 m^-3"

**Result**: **0 papers found** ❌

**Why?**
```
Step 1: ✓ NLP Parser understands query
        → Extracts: type=density, min=1e19

Step 2: ✓ SPARQL Builder creates valid query
        → SELECT ... WHERE { ?dens a :Density ... }

Step 3: ✗ Fuseki finds NO density measurements
        → Returns empty result set

Step 4: ✓ API handles empty results gracefully
        → Returns {"papers": [], "total_results": 0}

Step 5: ✓ Frontend shows "No results found"
```

### Temperature Query Example

**Query**: "Show papers with temperature above 1 keV"

**Result**: **3 papers found** ✓

**Why?**
```
Step 1: ✓ NLP Parser understands query
        → Extracts: type=temperature, min=1.0 keV

Step 2: ✓ SPARQL Builder creates query
        → SELECT ... WHERE { ?temp a :Temperature ... }

Step 3: ✓ Fuseki finds 3 matching papers
        Paper 1: temp=1000 eV = 1.0 keV
        Paper 2: temp=30 keV
        Paper 3: temp=5.5 keV

Step 4: ✓ API deduplicates (if paper had multiple temps)
        → Returns unique papers only

Step 5: ✓ Frontend displays 3 unique papers
```

---

## Checking What Parameters You Have

### Via API

```bash
# Check statistics
curl http://localhost:8000/statistics
```

**Response shows:**
```json
{
  "papers": 300,
  "temperature": {
    "count": 30,        ← You have temperature data
    "avg_kev": 1.085,
    "max_kev": 30.0,
    "min_kev": 0.0
  },
  "density": {
    "count": 0,         ← No density data!
    "avg_density": null,
    "max_density": null,
    "min_density": null
  }
}
```

### Via Data Files

```bash
# Check extracted parameters
python3 << 'EOF'
import json

with open('data/extracted_with_llm.json') as f:
    data = json.load(f)

# Count by parameter type
temp_count = sum(len(d['parameters']['temperature']) for d in data)
dens_count = sum(len(d['parameters']['density']) for d in data)

print(f"Temperature measurements: {temp_count}")
print(f"Density measurements: {dens_count}")

# Show papers with each type
papers_with_temp = [d for d in data if d['parameters']['temperature']]
papers_with_dens = [d for d in data if d['parameters']['density']]

print(f"\nPapers with temperature: {len(papers_with_temp)}")
print(f"Papers with density: {len(papers_with_dens)}")

# Show example
if papers_with_temp:
    print(f"\nExample temp measurement:")
    sample = papers_with_temp[0]
    print(f"  Paper: {sample['title'][:60]}")
    print(f"  Temps: {sample['parameters']['temperature']}")
EOF
```

### Via Knowledge Graph (TTL)

```bash
# Count temperature triples
grep -c ":Temperature" data/plasma_data.ttl

# Count density triples
grep -c ":Density" data/plasma_data.ttl

# Show example
grep -A 5 "a :Temperature" data/plasma_data.ttl | head -20
```

---

## How to Add Density Data

### Step 1: Check Current Papers

```bash
# Search for papers that mention density
python3 << 'EOF'
import json

with open('data/papers.json') as f:
    papers = json.load(f)

# Find papers mentioning density
density_papers = [
    p for p in papers
    if 'density' in p['abstract'].lower()
]

print(f"Papers mentioning 'density': {len(density_papers)}/{len(papers)}")

# Show first few
for paper in density_papers[:3]:
    print(f"\n{paper['id']}: {paper['title'][:60]}")
    # Check if abstract has actual density values
    import re
    dens_pattern = r'\d+\.?\d*\s*[×x]\s*10\^?\d+\s*(m\^?-?3|cm\^?-?3)'
    matches = re.findall(dens_pattern, paper['abstract'])
    print(f"  Density patterns found: {len(matches)}")
EOF
```

### Step 2: Improve Extraction

If papers have density but extraction failed, improve the patterns:

**Edit `scripts/extract_parameters.py`:**

```python
DENSITY_PATTERNS = [
    # Add more flexible patterns
    r'(?:density|n_?e|n_?i)[\s:=~]*(?:of|about|approximately|around)?[\s]*(\d+\.?\d*)[\s]*[×x]\s*10[\^]?([+-]?\d+)[\s]*(m\^?-?3|cm\^?-?3)',

    # Handle scientific notation variations
    r'(\d+\.?\d*)\s*[×x]\s*10[\^⁰¹²³⁴⁵⁶⁷⁸⁹\-]?(\d+)[\s]*(m\^?-?3|cm\^?-?3)',

    # Handle different formats
    r'n_?e\s*=\s*(\d+\.?\d*)\s*[×x]\s*10[\^]?(\d+)',
]
```

### Step 3: Re-extract and Rebuild

```bash
# Re-extract with improved patterns
python3 scripts/extract_parameters.py \
  --input data/papers.json \
  --output data/extracted_with_llm.json

# Check if density improved
python3 -c "
import json
data = json.load(open('data/extracted_with_llm.json'))
dens_count = sum(len(d['parameters']['density']) for d in data)
print(f'Density measurements now: {dens_count}')
"

# Rebuild knowledge graph
python3 scripts/build_knowledge_graph.py

# Reload into Fuseki
docker-compose restart fuseki
```

---

## Query Examples by Parameter Type

### Temperature Queries (Will Work ✓)

```bash
# Natural language
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "Papers with temperature above 1 keV", "limit": 10}'

# Direct API
curl "http://localhost:8000/temperatures?min_temp=1.0"

# SPARQL
curl -X POST http://localhost:3030/plasma/query \
  -H "Content-Type: application/sparql-query" \
  --data "PREFIX : <http://example.org/plasma#>
SELECT * WHERE { ?temp a :Temperature } LIMIT 10"
```

### Density Queries (Won't Work Yet ✗)

```bash
# Natural language - returns empty
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "Papers with density above 1e19", "limit": 10}'

# Direct API - returns empty array
curl "http://localhost:8000/densities?min_density=1e19"

# SPARQL - returns empty
curl -X POST http://localhost:3030/plasma/query \
  -H "Content-Type: application/sparql-query" \
  --data "PREFIX : <http://example.org/plasma#>
SELECT * WHERE { ?dens a :Density } LIMIT 10"
```

---

## Summary

### What Works Now ✓
- Temperature queries
- 30 temperature measurements
- 18 papers with temperature data
- Range queries (min/max temperature)
- Natural language understanding
- **No duplicate results** (fixed!)

### What Doesn't Work Yet ✗
- Density queries (no data)
- Combined temp + density queries
- Density statistics

### To Enable Density Queries
1. Improve extraction patterns
2. Or collect different papers
3. Or manually annotate existing papers
4. Then rebuild and reload

### Current Queryable Data

**You can search for:**
- Papers with temperature measurements ✓
- Temperature ranges (0.0 - 30.0 keV) ✓
- Specific units (eV, keV, K) ✓
- Recent papers with temperature ✓

**You cannot search for (yet):**
- Density measurements ✗
- Density ranges ✗
- Combined temp+density ✗
