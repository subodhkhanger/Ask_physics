#!/bin/bash
set -e

# Use Railway PORT or default to 3030
FUSEKI_PORT=${PORT:-3030}
echo "Starting Fuseki on port $FUSEKI_PORT..."

# Start Fuseki in background with configuration file
# IMPORTANT: Set FUSEKI_HOST to bind to all interfaces (0.0.0.0) for Railway
export FUSEKI_HOST=0.0.0.0
./fuseki-server --port=$FUSEKI_PORT --config=/opt/fuseki/config.ttl &
FUSEKI_PID=$!

echo "Waiting for Fuseki to start..."
# Wait for Fuseki to be ready by checking the ping endpoint
for i in {1..30}; do
  if curl -s http://localhost:$FUSEKI_PORT/\$/ping > /dev/null 2>&1; then
    echo "Fuseki is ready!"
    break
  fi
  echo "Attempt $i: Fuseki not ready yet, waiting..."
  sleep 2
done

sleep 3

echo "Checking available datasets..."
DATASETS_JSON=$(curl -s http://localhost:$FUSEKI_PORT/\$/datasets)
echo "$DATASETS_JSON"

# Check if /plasma dataset exists
if echo "$DATASETS_JSON" | grep -q '"ds.name" : "/plasma"'; then
  echo "✓ /plasma dataset found"
else
  echo "✗ WARNING: /plasma dataset NOT found!"
  echo "Available datasets:"
  echo "$DATASETS_JSON" | grep -o '"ds.name" : "[^"]*"' || echo "No datasets found"
fi

sleep 2

echo "Testing /plasma/query endpoint..."
TEST_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:$FUSEKI_PORT/plasma/query \
  -H "Accept: application/sparql-results+json" \
  --data-urlencode "query=SELECT * WHERE { ?s ?p ?o } LIMIT 1")
HTTP_CODE=$(echo "$TEST_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
echo "Query endpoint returned HTTP $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
  echo "✓ /plasma/query endpoint is accessible"
else
  echo "✗ WARNING: /plasma/query endpoint returned HTTP $HTTP_CODE"
fi

sleep 2

echo "Loading ontology..."
if curl -f -X POST -H "Content-Type: text/turtle" \
  --data-binary "@/opt/fuseki/ontology/plasma_physics.ttl" \
  http://localhost:$FUSEKI_PORT/plasma/data 2>&1; then
  echo "✓ Ontology loaded successfully!"
else
  echo "✗ Warning: Ontology load failed"
fi

sleep 2

echo "Loading data..."
if curl -f -X POST -H "Content-Type: text/turtle" \
  --data-binary "@/opt/fuseki/data/plasma_data.ttl" \
  http://localhost:$FUSEKI_PORT/plasma/data 2>&1; then
  echo "✓ Data loaded successfully!"
else
  echo "✗ Warning: Data load failed"
fi

sleep 2

echo "Verifying data loaded..."
QUERY_RESPONSE=$(curl -s -X POST http://localhost:$FUSEKI_PORT/plasma/query \
  -H "Accept: application/sparql-results+json" \
  --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")

# Extract the count value from JSON response
TRIPLE_COUNT=$(echo "$QUERY_RESPONSE" | grep -oP '"value"\s*:\s*"\K[0-9]+' | head -1)

# Fallback if grep -P not available
if [ -z "$TRIPLE_COUNT" ]; then
  TRIPLE_COUNT=$(echo "$QUERY_RESPONSE" | sed -n 's/.*"value"[[:space:]]*:[[:space:]]*"\([0-9]*\)".*/\1/p' | head -1)
fi

echo "Total triples in dataset: ${TRIPLE_COUNT:-0}"

if [ -n "$TRIPLE_COUNT" ] && [ "$TRIPLE_COUNT" -gt "0" ]; then
  echo "✓ Dataset verification successful! ($TRIPLE_COUNT triples)"
else
  echo "✗ Warning: No triples found in dataset"
  echo "Query response: $QUERY_RESPONSE"
fi

echo ""
echo "================================================"
echo "Fuseki ready on port $FUSEKI_PORT!"
echo "Public endpoint: http://0.0.0.0:$FUSEKI_PORT/plasma/query"
echo "Datasets available: /plasma"
echo "================================================"

# Keep Fuseki running in foreground
wait $FUSEKI_PID
