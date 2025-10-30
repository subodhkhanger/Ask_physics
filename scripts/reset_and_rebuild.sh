#!/bin/bash

# ============================================
# Reset and Rebuild askPhysics Data Pipeline
# ============================================
# This script cleans all data and rebuilds the knowledge graph from scratch
#
# Usage:
#   ./scripts/reset_and_rebuild.sh
#   ./scripts/reset_and_rebuild.sh --skip-collect  # Use existing papers.json

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKIP_COLLECT=false
PAPER_LIMIT=300

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-collect)
            SKIP_COLLECT=true
            shift
            ;;
        --limit)
            PAPER_LIMIT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-collect] [--limit N]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Reset and Rebuild askPhysics Pipeline${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ============================================
# Step 1: Backup existing data
# ============================================
echo -e "${YELLOW}[1/6] Creating backup of existing data...${NC}"

BACKUP_DIR="data/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "data/papers.json" ]; then
    cp data/papers.json "$BACKUP_DIR/" && echo "  ✓ Backed up papers.json"
fi

if [ -f "data/extracted_with_llm.json" ]; then
    cp data/extracted_with_llm.json "$BACKUP_DIR/" && echo "  ✓ Backed up extracted_with_llm.json"
fi

if [ -f "data/plasma_data.ttl" ]; then
    cp data/plasma_data.ttl "$BACKUP_DIR/" && echo "  ✓ Backed up plasma_data.ttl"
fi

echo -e "${GREEN}  Backup saved to: $BACKUP_DIR${NC}"
echo ""

# ============================================
# Step 2: Clean existing data (optional)
# ============================================
if [ "$SKIP_COLLECT" = false ]; then
    echo -e "${YELLOW}[2/6] Cleaning existing data files...${NC}"

    # Remove old data files
    rm -f data/extracted_with_llm.json && echo "  ✓ Removed extracted_with_llm.json"
    rm -f data/plasma_data.ttl && echo "  ✓ Removed plasma_data.ttl"

    echo -e "${GREEN}  Data files cleaned${NC}"
    echo ""
else
    echo -e "${YELLOW}[2/6] Skipping data collection (using existing papers.json)...${NC}"
    echo ""
fi

# ============================================
# Step 3: Collect papers (if not skipped)
# ============================================
if [ "$SKIP_COLLECT" = false ]; then
    echo -e "${YELLOW}[3/6] Collecting papers from arXiv (limit: $PAPER_LIMIT)...${NC}"

    # Remove old papers file
    rm -f data/papers.json

    # Collect new papers
    python3 scripts/collect_papers_with_params.py --limit "$PAPER_LIMIT" --output data/papers.json

    echo -e "${GREEN}  Papers collected successfully${NC}"
    echo ""
else
    echo -e "${YELLOW}[3/6] Using existing papers.json...${NC}"

    if [ ! -f "data/papers.json" ]; then
        echo -e "${RED}  Error: data/papers.json not found!${NC}"
        exit 1
    fi

    PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('data/papers.json'))))")
    echo -e "${GREEN}  Found $PAPER_COUNT papers${NC}"
    echo ""
fi

# ============================================
# Step 4: Deduplicate papers
# ============================================
echo -e "${YELLOW}[4/6] Deduplicating papers...${NC}"

python3 scripts/deduplicate_data.py --no-backup

echo -e "${GREEN}  Papers deduplicated${NC}"
echo ""

# ============================================
# Step 5: Extract parameters with LLM
# ============================================
echo -e "${YELLOW}[5/6] Extracting parameters with LLM...${NC}"

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}  Warning: OPENAI_API_KEY not set. Using regex-only extraction.${NC}"
    echo -e "${RED}  For better accuracy, set OPENAI_API_KEY in .env file${NC}"
    python3 scripts/extract_parameters.py --input data/papers.json --output data/extracted_with_llm.json --no-llm
else
    echo -e "${GREEN}  Using LLM validation for higher accuracy${NC}"
    python3 scripts/extract_parameters.py --input data/papers.json --output data/extracted_with_llm.json
fi

echo -e "${GREEN}  Parameter extraction complete${NC}"
echo ""

# ============================================
# Step 6: Build knowledge graph
# ============================================
echo -e "${YELLOW}[6/6] Building knowledge graph (TTL file)...${NC}"

# Check if build_knowledge_graph.py exists
if [ -f "scripts/build_knowledge_graph.py" ]; then
    python3 scripts/build_knowledge_graph.py --input data/extracted_with_llm.json --output data/plasma_data.ttl
elif [ -f "scripts/build_kg.py" ]; then
    python3 scripts/build_kg.py --input data/extracted_with_llm.json --output data/plasma_data.ttl
else
    # Create a basic TTL builder if it doesn't exist
    echo -e "${YELLOW}  Knowledge graph builder not found, creating basic version...${NC}"
    python3 << 'EOF'
import json
from datetime import datetime

# Load extracted data
with open('data/extracted_with_llm.json', 'r') as f:
    data = json.load(f)

# Count papers with parameters
papers_with_params = [d for d in data if d['parameters']['temperature'] or d['parameters']['density']]

# Generate TTL
ttl_content = f"""@prefix : <http://example.org/plasma#> .
@prefix paper: <http://example.org/plasma/paper/> .
@prefix meas: <http://example.org/plasma/measurement/> .
@prefix param: <http://example.org/plasma/parameter/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# ============================================
# Plasma Physics Knowledge Graph Data
# Generated: {datetime.now().isoformat()}
# Papers: {len(papers_with_params)}
# ============================================

"""

meas_counter = 1
param_counter = 1

for entry in papers_with_params:
    paper_id = entry['paper_id']
    ttl_content += f"\n# Paper: {entry['title']}\n"
    ttl_content += f"<http://example.org/plasma/paper/{paper_id}> a :Paper ;\n"
    ttl_content += f'    :arxivId "{paper_id}" ;\n'
    ttl_content += f'    :title "{entry["title"]}" ;\n'

    # Add measurements
    for temp in entry['parameters']['temperature']:
        ttl_content += f"    :reports <http://example.org/plasma/measurement/m{meas_counter}> ;\n"
        meas_counter += 1

    for dens in entry['parameters']['density']:
        ttl_content += f"    :reports <http://example.org/plasma/measurement/m{meas_counter}> ;\n"
        meas_counter += 1

    ttl_content = ttl_content.rstrip(' ;\n') + ' .\n'

# Save TTL file
with open('data/plasma_data.ttl', 'w') as f:
    f.write(ttl_content)

print(f"Generated TTL file with {len(papers_with_params)} papers")
EOF
fi

echo -e "${GREEN}  Knowledge graph built successfully${NC}"
echo ""

# ============================================
# Step 7: Verify and display summary
# ============================================
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}============================================${NC}"

# Count papers
if [ -f "data/papers.json" ]; then
    PAPER_COUNT=$(python3 -c "import json; print(len(json.load(open('data/papers.json'))))" 2>/dev/null || echo "?")
    echo -e "${GREEN}Papers collected: $PAPER_COUNT${NC}"
fi

# Count extractions
if [ -f "data/extracted_with_llm.json" ]; then
    python3 << 'EOF'
import json
data = json.load(open('data/extracted_with_llm.json'))
papers_with_params = [d for d in data if d['parameters']['temperature'] or d['parameters']['density']]
total_temps = sum(len(d['parameters']['temperature']) for d in data)
total_dens = sum(len(d['parameters']['density']) for d in data)
print(f"Papers with parameters: {len(papers_with_params)}/{len(data)}")
print(f"Temperature measurements: {total_temps}")
print(f"Density measurements: {total_dens}")
EOF
fi

# Check TTL file
if [ -f "data/plasma_data.ttl" ]; then
    TTL_SIZE=$(du -h data/plasma_data.ttl | cut -f1)
    echo -e "${GREEN}Knowledge graph: $TTL_SIZE${NC}"
fi

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "1. ${YELLOW}Load data into Fuseki:${NC}"
echo -e "   ${GREEN}docker-compose restart fuseki${NC}"
echo -e "   or manually upload data/plasma_data.ttl to Fuseki"
echo ""
echo -e "2. ${YELLOW}Start the backend:${NC}"
echo -e "   ${GREEN}cd backend && python run.py${NC}"
echo ""
echo -e "3. ${YELLOW}Test the API:${NC}"
echo -e "   ${GREEN}curl http://localhost:8000/health${NC}"
echo ""
echo -e "${GREEN}✓ Pipeline rebuild complete!${NC}"
