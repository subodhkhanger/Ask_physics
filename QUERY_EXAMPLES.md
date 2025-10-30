# Query Examples for askPhysics

This document shows example queries you can use with your askPhysics database.

---

## Current Database Contents

**Papers**: 300 total
**Papers with measurements**: 18
**Temperature measurements**: 30
**Density measurements**: 0 (not yet extracted)

**Temperature range**: 0.000 - 30.000 keV

---

## 1. REST API Queries

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "fuseki_connected": true,
  "version": "1.0.0"
}
```

### Get Statistics

```bash
curl http://localhost:8000/statistics
```

**Response:**
```json
{
  "papers": 300,
  "temperature": {
    "count": 30,
    "avg_kev": 1.085,
    "max_kev": 30.0,
    "min_kev": 0.0
  },
  "density": {
    "count": 0,
    "avg_density": null,
    "max_density": null,
    "min_density": null
  }
}
```

### List All Papers

```bash
curl "http://localhost:8000/papers?limit=10&offset=0"
```

**Parameters:**
- `limit`: Number of papers to return (1-100)
- `offset`: Pagination offset

### Get Temperature Measurements

```bash
# All temperatures
curl http://localhost:8000/temperatures

# Temperatures above 1 keV
curl "http://localhost:8000/temperatures?min_temp=1.0"

# Temperatures between 0.1 and 10 keV
curl "http://localhost:8000/temperatures?min_temp=0.1&max_temp=10.0"

# Limit results
curl "http://localhost:8000/temperatures?limit=5"
```

**Example Response:**
```json
[
  {
    "arxiv_id": "2510.10112v1",
    "title": "Thermal and Electrical Conductivities of Aluminum Up to 1000 eV",
    "value": 1000.0,
    "unit": "eV",
    "normalized_value": 1.0,
    "confidence": "medium",
    "context": "...aluminum up to 1000 eV..."
  }
]
```

### Search Papers

```bash
# Search by keyword
curl "http://localhost:8000/papers/search?q=plasma&limit=10"

# Search for tokamak papers
curl "http://localhost:8000/papers/search?q=tokamak&limit=20"
```

---

## 2. Natural Language Queries

The most powerful feature! Send natural language queries:

### Basic Temperature Query

```bash
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me papers with temperature measurements",
    "limit": 10
  }'
```

### Temperature Range Query

```bash
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find papers with temperature above 1 keV",
    "limit": 10
  }'
```

```bash
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Papers with temperature between 0.1 and 10 keV",
    "limit": 20
  }'
```

### With SPARQL Debug

```bash
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show papers with high temperature above 5 keV",
    "limit": 5,
    "include_sparql": true
  }'
```

**Response includes:**
```json
{
  "parsed_query": {
    "intent": "search",
    "parameters": {
      "temperature": {
        "min": 5.0,
        "max": null,
        "unit": "keV",
        "normalized_min": 5.0,
        "normalized_max": null
      }
    },
    "keywords": ["high", "temperature"],
    "temporal_constraint": null
  },
  "papers": [...],
  "total_results": 3,
  "generated_sparql": "PREFIX : <http://example.org/plasma#>...",
  "execution_time_ms": 45.23
}
```

### Keyword Queries

```bash
# Recent papers
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Recent tokamak experiments",
    "limit": 10
  }'

# Specific topics
curl -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Papers about plasma confinement",
    "limit": 10
  }'
```

---

## 3. Direct SPARQL Queries

You can also query the Fuseki endpoint directly:

### List All Papers with Temperatures

```sparql
PREFIX : <http://example.org/plasma#>

SELECT DISTINCT ?paper ?title ?arxivId
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :arxivId ?arxivId ;
         :reports ?measurement .
  ?measurement :measuresParameter ?param .
  ?param a :Temperature .
}
LIMIT 20
```

**Execute via curl:**
```bash
curl -X POST http://localhost:3030/plasma/query \
  -H "Content-Type: application/sparql-query" \
  --data-binary @- << 'EOF'
PREFIX : <http://example.org/plasma#>
SELECT DISTINCT ?paper ?title ?arxivId
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :arxivId ?arxivId ;
         :reports ?measurement .
  ?measurement :measuresParameter ?param .
  ?param a :Temperature .
}
LIMIT 20
EOF
```

### Get Temperatures Above Threshold

```sparql
PREFIX : <http://example.org/plasma#>

SELECT ?arxivId ?title ?tempValue ?tempUnit ?normalizedValue
WHERE {
  ?paper a :Paper ;
         :arxivId ?arxivId ;
         :title ?title ;
         :reports ?measurement .

  ?measurement :measuresParameter ?temp .

  ?temp a :Temperature ;
        :value ?tempValue ;
        :unitString ?tempUnit ;
        :normalizedValue ?normalizedValue .

  FILTER(?normalizedValue > 1.0)
}
ORDER BY DESC(?normalizedValue)
LIMIT 10
```

### Count Measurements by Confidence

```sparql
PREFIX : <http://example.org/plasma#>

SELECT ?confidence (COUNT(?measurement) as ?count)
WHERE {
  ?measurement a :Measurement ;
               :confidence ?confidence .
}
GROUP BY ?confidence
```

### Get Temperature Statistics

```sparql
PREFIX : <http://example.org/plasma#>

SELECT
  (COUNT(?temp) as ?count)
  (AVG(?normValue) as ?avgKeV)
  (MAX(?normValue) as ?maxKeV)
  (MIN(?normValue) as ?minKeV)
WHERE {
  ?temp a :Temperature ;
        :normalizedValue ?normValue .
}
```

---

## 4. Example Natural Language Queries You Can Try

Based on your current data (18 papers with temperatures):

### Working Queries (Have Data)

✓ "Show me all papers with temperature measurements"
✓ "Papers with temperature above 1 keV"
✓ "Find high temperature experiments above 5 keV"
✓ "Papers with temperature between 0.1 and 10 keV"
✓ "Show recent research with temperature data"
✓ "Papers about plasma experiments"

### Queries That Won't Return Results (No Data Yet)

✗ "Papers with density measurements" (no density data)
✗ "High density plasma above 10^19 m^-3" (no density data)
✗ "Papers with both temperature and density" (no density data)

---

## 5. Adding Density Data

Currently, you have **0 density measurements**. To add density data:

### Option 1: Improve Extraction Patterns

Edit `scripts/extract_parameters.py` to better match density patterns:

```python
DENSITY_PATTERNS = [
    # Current patterns may not be matching your papers
    # Add more flexible patterns
]
```

### Option 2: Collect Different Papers

Collect papers that explicitly mention density:

```bash
python3 scripts/collect_papers_with_params.py \
  --limit 100 \
  --output data/papers.json
```

Then re-extract:

```bash
python3 scripts/extract_parameters.py \
  --input data/papers.json \
  --output data/extracted_with_llm.json

python3 scripts/build_knowledge_graph.py
```

### Option 3: Manual Annotation

For critical papers, manually add density measurements to the JSON.

---

## 6. Testing Queries

### Quick Test Script

Create `test_queries.sh`:

```bash
#!/bin/bash

echo "Testing askPhysics API..."

# Test 1: Health
echo -e "\n1. Health Check:"
curl -s http://localhost:8000/health | jq '.'

# Test 2: Statistics
echo -e "\n2. Statistics:"
curl -s http://localhost:8000/statistics | jq '.'

# Test 3: Natural language query
echo -e "\n3. Natural Language Query:"
curl -s -X POST http://localhost:8000/query/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show papers with temperature above 1 keV",
    "limit": 5
  }' | jq '.total_results, .papers[0].title'

echo -e "\n✓ All tests complete"
```

Make executable and run:
```bash
chmod +x test_queries.sh
./test_queries.sh
```

---

## 7. Python Client Example

```python
import requests

# Base URL
API_URL = "http://localhost:8000"

# Natural language query
def query_papers(query_text, limit=10):
    response = requests.post(
        f"{API_URL}/query/natural-language",
        json={
            "query": query_text,
            "limit": limit,
            "include_sparql": False
        }
    )
    return response.json()

# Example usage
result = query_papers("Papers with temperature above 1 keV", limit=5)
print(f"Found {result['total_results']} papers")
for paper in result['papers']:
    print(f"  - {paper['title']}")

# Get temperature measurements
def get_temperatures(min_temp=None, max_temp=None):
    params = {}
    if min_temp:
        params['min_temp'] = min_temp
    if max_temp:
        params['max_temp'] = max_temp

    response = requests.get(f"{API_URL}/temperatures", params=params)
    return response.json()

# Example
temps = get_temperatures(min_temp=1.0)
print(f"\nTemperatures above 1 keV: {len(temps)}")
```

---

## Current Database Summary

```
Papers with measurements by parameter type:
  Temperature: 18 papers, 30 measurements
  Density: 0 papers, 0 measurements

Temperature distribution:
  eV: 13 measurements
  k: 10 measurements
  K: 5 measurements
  keV: 1 measurement
  kJ: 1 measurement

Example papers in database:
  - "The Opacity Project: R-Matrix Calculations..."
  - "Physics insights from a large-scale 2D UEDGE..."
  - "Thermal and Electrical Conductivities of Aluminum..."
  - (15 more...)
```

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs
- **Fuseki Interface**: http://localhost:3030
- **Query Builder**: See `backend/query_builder.py`
- **NLP Parser**: See `backend/nlp_query_processor.py`
