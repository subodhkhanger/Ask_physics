#!/bin/bash

# ============================================
# Reload Fuseki with Clean Data
# ============================================
# This script clears the Fuseki database and reloads fresh data

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FUSEKI_URL="${FUSEKI_URL:-http://localhost:3030}"
DATASET="${FUSEKI_DATASET:-plasma}"
TTL_FILE="${TTL_FILE:-data/plasma_data.ttl}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Reload Fuseki Database${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "Fuseki URL: $FUSEKI_URL"
echo "Dataset: $DATASET"
echo "TTL File: $TTL_FILE"
echo ""

# Check if TTL file exists
if [ ! -f "$TTL_FILE" ]; then
    echo -e "${RED}Error: TTL file not found: $TTL_FILE${NC}"
    echo "Run: python3 scripts/build_knowledge_graph.py"
    exit 1
fi

# Check file size
TTL_SIZE=$(du -h "$TTL_FILE" | cut -f1)
echo -e "${GREEN}✓ TTL file found: $TTL_SIZE${NC}"
echo ""

# Step 1: Check if Fuseki is running
echo -e "${YELLOW}[1/4] Checking Fuseki connection...${NC}"
if curl -sf "$FUSEKI_URL/$/ping" > /dev/null; then
    echo -e "${GREEN}  ✓ Fuseki is running${NC}"
else
    echo -e "${RED}  ✗ Fuseki is not responding${NC}"
    echo ""
    echo "Start Fuseki with: docker-compose up -d fuseki"
    exit 1
fi
echo ""

# Step 2: Clear existing data
echo -e "${YELLOW}[2/4] Clearing existing data from dataset '$DATASET'...${NC}"

# Try to delete all triples
DELETE_QUERY="DELETE WHERE { ?s ?p ?o }"

curl -s -X POST "$FUSEKI_URL/$DATASET/update" \
    -H "Content-Type: application/sparql-update" \
    --data-urlencode "update=$DELETE_QUERY" \
    > /dev/null 2>&1 || {
    echo -e "${YELLOW}  Warning: Could not delete via SPARQL UPDATE${NC}"
    echo -e "${YELLOW}  Trying to drop and recreate graph...${NC}"

    # Alternative: Drop the default graph
    DROP_QUERY="DROP DEFAULT"
    curl -s -X POST "$FUSEKI_URL/$DATASET/update" \
        -H "Content-Type: application/sparql-update" \
        --data-urlencode "update=$DROP_QUERY" \
        > /dev/null 2>&1 || true
}

echo -e "${GREEN}  ✓ Data cleared${NC}"
echo ""

# Step 3: Verify it's empty
echo -e "${YELLOW}[3/4] Verifying database is empty...${NC}"
COUNT_QUERY="SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
COUNT=$(curl -s -X POST "$FUSEKI_URL/$DATASET/query" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$COUNT_QUERY" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

echo -e "  Triples remaining: $COUNT"
if [ "$COUNT" -eq "0" ]; then
    echo -e "${GREEN}  ✓ Database is empty${NC}"
else
    echo -e "${YELLOW}  Warning: $COUNT triples still present (may be OK)${NC}"
fi
echo ""

# Step 4: Upload new data
echo -e "${YELLOW}[4/4] Uploading new data from $TTL_FILE...${NC}"

UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$FUSEKI_URL/$DATASET/data" \
    -H "Content-Type: text/turtle" \
    --data-binary "@$TTL_FILE")

HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" -eq "200" ] || [ "$HTTP_CODE" -eq "201" ]; then
    echo -e "${GREEN}  ✓ Data uploaded successfully${NC}"
else
    echo -e "${RED}  ✗ Upload failed with HTTP $HTTP_CODE${NC}"
    echo "$UPLOAD_RESPONSE" | head -n -1
    exit 1
fi
echo ""

# Verify new data
echo -e "${YELLOW}Verifying new data...${NC}"

# Count papers
PAPERS_QUERY="PREFIX : <http://example.org/plasma#> SELECT (COUNT(DISTINCT ?paper) as ?count) WHERE { ?paper a :Paper }"
PAPERS=$(curl -s -X POST "$FUSEKI_URL/$DATASET/query" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$PAPERS_QUERY" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

# Count temperatures
TEMPS_QUERY="PREFIX : <http://example.org/plasma#> SELECT (COUNT(?temp) as ?count) WHERE { ?temp a :Temperature }"
TEMPS=$(curl -s -X POST "$FUSEKI_URL/$DATASET/query" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$TEMPS_QUERY" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

# Get temperature statistics
STATS_QUERY="PREFIX : <http://example.org/plasma#> SELECT (AVG(?v) as ?avg) (MAX(?v) as ?max) (MIN(?v) as ?min) WHERE { ?temp a :Temperature ; :normalizedValue ?v }"
STATS=$(curl -s -X POST "$FUSEKI_URL/$DATASET/query" \
    -H "Accept: application/sparql-results+json" \
    --data-urlencode "query=$STATS_QUERY" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
b = data['results']['bindings'][0]
avg = float(b.get('avg', {}).get('value', 0))
max_v = float(b.get('max', {}).get('value', 0))
min_v = float(b.get('min', {}).get('value', 0))
print(f'{avg:.4f} {max_v:.4f} {min_v:.4f}')
" 2>/dev/null || echo "0 0 0")

AVG=$(echo $STATS | cut -d' ' -f1)
MAX=$(echo $STATS | cut -d' ' -f2)
MIN=$(echo $STATS | cut -d' ' -f3)

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Database Status${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}Papers: $PAPERS${NC}"
echo -e "${GREEN}Temperature measurements: $TEMPS${NC}"
echo -e "${GREEN}Temperature avg: $AVG keV${NC}"
echo -e "${GREEN}Temperature max: $MAX keV${NC}"
echo -e "${GREEN}Temperature min: $MIN keV${NC}"
echo ""

# Check for suspicious values
if (( $(echo "$MAX > 1000" | bc -l) )); then
    echo -e "${RED}⚠️  WARNING: Maximum temperature is suspiciously high!${NC}"
    echo -e "${RED}   This suggests data corruption or incorrect normalization${NC}"
    echo ""
elif (( $(echo "$MAX < 0.001" | bc -l) )); then
    echo -e "${RED}⚠️  WARNING: Maximum temperature is suspiciously low!${NC}"
    echo -e "${RED}   This suggests incorrect normalization${NC}"
    echo ""
else
    echo -e "${GREEN}✓ Data looks reasonable${NC}"
    echo ""
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}============================================${NC}"
echo "1. Restart backend: docker-compose restart backend"
echo "2. Test API: curl http://localhost:8000/statistics"
echo "3. Check frontend for corrected values"
echo ""
echo -e "${GREEN}✓ Fuseki reload complete!${NC}"
