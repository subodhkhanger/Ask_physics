# Plasma Physics Literature Search - Quick Start Guide

## What is This?

A knowledge graph system for querying plasma physics experimental parameters from scientific literature. Extract temperature, density, and other measurements from papers and query them using SPARQL.

## Prerequisites

- Docker Desktop installed ([download](https://www.docker.com/products/docker-desktop))
- Python 3.8+ installed
- Terminal/Command Line access

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Knowledge Graph

```bash
# Start Apache Jena Fuseki and load data
bash scripts/setup_fuseki.sh
```

This will:
- Start Fuseki triple store on port 3030
- Create a dataset named "plasma"
- Load the ontology and data
- Take ~30 seconds

### 3. Access the System

**Web UI**: http://localhost:3030
- Username: `admin`
- Password: `admin123`

**Query Endpoint**: http://localhost:3030/plasma/query

### 4. Run Your First Query

**Option A: Web UI**
1. Go to http://localhost:3030
2. Click "query" under "plasma" dataset
3. Paste this query:

```sparql
PREFIX : <http://example.org/plasma#>

SELECT ?title ?temp ?unit
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :reports ?meas .

  ?meas :measuresParameter ?param .

  ?param a :Temperature ;
         :value ?temp ;
         :unitString ?unit .
}
LIMIT 10
```

4. Click "Execute"

**Option B: Python Script**

```bash
python scripts/test_sparql.py
```

**Option C: cURL**

```bash
curl -X POST http://localhost:3030/plasma/query \
  --data-urlencode "query=PREFIX : <http://example.org/plasma#> SELECT (COUNT(?p) as ?count) WHERE { ?p a :Paper }" \
  -H "Accept: application/sparql-results+json" \
  -u admin:admin123
```

## Example Queries

### Find High-Temperature Plasmas (> 10 keV)

```sparql
PREFIX : <http://example.org/plasma#>

SELECT ?title ?temp ?unit
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :reports ?meas .

  ?meas :measuresParameter ?param .

  ?param a :Temperature ;
         :value ?temp ;
         :normalizedValue ?normTemp .

  FILTER(?normTemp > 10)
}
ORDER BY DESC(?normTemp)
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

### Find Papers with Both Temp and Density

```sparql
PREFIX : <http://example.org/plasma#>

SELECT DISTINCT ?title ?temp ?dens
WHERE {
  ?paper a :Paper ;
         :title ?title ;
         :reports ?meas1 ;
         :reports ?meas2 .

  ?meas1 :measuresParameter ?tempParam .
  ?tempParam a :Temperature ;
             :value ?temp .

  ?meas2 :measuresParameter ?densParam .
  ?densParam a :Density ;
             :value ?dens .
}
```

## Project Structure

```
askPhysics/
├── data/                          # Data files
│   ├── sample_extracted_params.json   # Extracted parameters (input)
│   └── plasma_data.ttl                # RDF knowledge graph (output)
├── ontology/
│   └── plasma_physics.ttl         # Ontology definition
├── queries/
│   └── example_queries.sparql     # 12 example queries
├── scripts/
│   ├── collect_papers.py          # Collect papers from arXiv
│   ├── extract_parameters.py      # Extract temp/density
│   ├── convert_to_rdf.py          # Convert to RDF
│   ├── setup_fuseki.sh            # Setup Fuseki
│   └── test_sparql.py             # Test queries
├── docker-compose.yml             # Fuseki deployment
└── PHASE1_COMPLETE.md             # Phase 1 documentation
```

## Common Tasks

### Add New Papers

```bash
# 1. Collect papers from arXiv
python scripts/collect_papers_with_params.py --limit 20

# 2. Extract parameters
python scripts/extract_parameters.py \
  --input data/papers_filtered.json \
  --output data/extracted_params.json \
  --no-llm

# 3. Convert to RDF
python scripts/convert_to_rdf.py \
  --input data/extracted_params.json \
  --output data/plasma_data_new.ttl

# 4. Load into Fuseki
curl -X POST http://localhost:3030/plasma/data \
  -H "Content-Type: text/turtle" \
  --data-binary "@data/plasma_data_new.ttl" \
  -u admin:admin123
```

### Stop/Start Fuseki

```bash
# Stop
docker compose down

# Start
docker compose up -d

# View logs
docker compose logs -f
```

### Backup Data

```bash
# The Fuseki data is stored in ./fuseki-data/
tar -czf fuseki-backup.tar.gz fuseki-data/
```

## Troubleshooting

### Fuseki won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker compose logs

# Restart
docker compose down
docker compose up -d
```

### "Connection refused" error

- Fuseki takes ~10 seconds to start
- Wait and try again
- Check http://localhost:3030 in browser

### Query returns no results

- Verify data is loaded: Click "info" in Fuseki UI
- Should show ~373 triples
- Try simpler query: `SELECT * WHERE { ?s ?p ?o } LIMIT 10`

### Docker not installed

Install from: https://www.docker.com/products/docker-desktop

## Next Steps

1. **Explore More Queries**: See [queries/example_queries.sparql](queries/example_queries.sparql)
2. **Read Full Documentation**:
   - [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Data extraction
   - [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) - Knowledge graph
3. **Extend the System**:
   - Add more papers
   - Extract additional parameters
   - Build REST API (Phase 3)
   - Create visualization dashboard (Phase 4)

## Need Help?

- Check documentation: `README.md`
- View example queries: `queries/example_queries.sparql`
- Read ontology: `ontology/plasma_physics.ttl`
- Test connection: `python scripts/test_sparql.py`

## Current Dataset

- **Papers**: 10 sample papers
- **Temperature measurements**: 24
- **Density measurements**: 4
- **RDF triples**: 373
- **Temperature range**: 0.003 - 15 keV
- **Density range**: 5×10¹⁷ - 3.5×10²⁵ m⁻³

---

**Built with**: Apache Jena Fuseki, Python, RDF, SPARQL, Docker
**Status**: Phase 2 Complete ✅
