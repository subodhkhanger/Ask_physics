#!/bin/bash
# Setup script for Apache Jena Fuseki triple store

set -e

echo "=== Plasma Physics Knowledge Graph - Fuseki Setup ==="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "Step 1: Starting Fuseki container..."
docker compose up -d

echo "Waiting for Fuseki to start (10 seconds)..."
sleep 10

echo ""
echo "Step 2: Creating dataset 'plasma'..."
curl -X POST http://localhost:3030/$/datasets \
    --data "dbName=plasma&dbType=tdb2" \
    -u admin:admin123 \
    -s -o /dev/null -w "HTTP Status: %{http_code}\n"

echo ""
echo "Step 3: Loading ontology..."
curl -X POST http://localhost:3030/plasma/data \
    -H "Content-Type: text/turtle" \
    --data-binary "@ontology/plasma_physics.ttl" \
    -u admin:admin123 \
    -s -o /dev/null -w "HTTP Status: %{http_code}\n"

echo ""
echo "Step 4: Loading data..."
curl -X POST http://localhost:3030/plasma/data \
    -H "Content-Type: text/turtle" \
    --data-binary "@data/plasma_data.ttl" \
    -u admin:admin123 \
    -s -o /dev/null -w "HTTP Status: %{http_code}\n"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Access Fuseki:"
echo "  Web UI:        http://localhost:3030"
echo "  Query endpoint: http://localhost:3030/plasma/query"
echo "  Username:      admin"
echo "  Password:      admin123"
echo ""
echo "To stop Fuseki:"
echo "  docker compose down"
echo ""
