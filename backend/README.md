# Plasma Physics API - Backend

REST API for querying plasma physics experimental parameters from scientific literature stored in an RDF knowledge graph.

## Features

- **FastAPI** - Modern, fast web framework
- **SPARQL Integration** - Query Apache Jena Fuseki triple store
- **Parameter Filtering** - Search by temperature and density ranges
- **Caching** - In-memory caching for improved performance
- **OpenAPI Documentation** - Interactive Swagger UI
- **Unit Tests** - Comprehensive test coverage

## Quick Start

### Prerequisites

- Python 3.10+
- Apache Jena Fuseki running (see root README.md)
- Virtual environment (recommended)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the backend directory (optional):

```bash
# Fuseki Configuration
FUSEKI_ENDPOINT=http://localhost:3030/plasma/query
FUSEKI_USERNAME=admin
FUSEKI_PASSWORD=admin123

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=300
```

### Run the API

```bash
# Development mode (with auto-reload)
python run.py

# Or use uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

```bash
GET /health
```

Check API and Fuseki connection status.

### Papers

```bash
# List all papers
GET /papers?limit=20&offset=0

# Get specific paper
GET /papers/{arxiv_id}

# Search papers
GET /papers/search?q=tokamak&limit=10
```

### Temperature Measurements

```bash
# Get all temperatures
GET /temperatures?limit=100

# Filter by range (in keV)
GET /temperatures?min_temp=5.0&max_temp=15.0&limit=50

# Get statistics
GET /temperatures/statistics
```

### Density Measurements

```bash
# Get all densities
GET /densities?limit=100

# Filter by range (in m^-3)
GET /densities?min_density=1e19&max_density=1e20&limit=50

# Get statistics
GET /densities/statistics
```

### Overall Statistics

```bash
# Get statistics for papers, temperatures, and densities
GET /statistics
```

## Example Requests

### Using cURL

```bash
# List papers
curl http://localhost:8000/papers

# Get temperature measurements above 10 keV
curl "http://localhost:8000/temperatures?min_temp=10"

# Search for tokamak papers
curl "http://localhost:8000/papers/search?q=tokamak"

# Get statistics
curl http://localhost:8000/statistics
```

### Using Python

```python
import requests

# List papers
response = requests.get("http://localhost:8000/papers")
papers = response.json()

# Filter temperatures
response = requests.get(
    "http://localhost:8000/temperatures",
    params={"min_temp": 5.0, "max_temp": 15.0}
)
temps = response.json()

# Get statistics
response = requests.get("http://localhost:8000/statistics")
stats = response.json()
print(f"Total papers: {stats['papers']}")
print(f"Avg temperature: {stats['temperature']['avg_kev']} keV")
```

### Using JavaScript

```javascript
// Fetch papers
fetch('http://localhost:8000/papers')
  .then(response => response.json())
  .then(data => console.log(data));

// Filter temperatures
fetch('http://localhost:8000/temperatures?min_temp=10')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_api.py

# Run with verbose output
pytest -v

# Run only integration tests (requires Fuseki)
pytest -m integration
```

### Manual Testing

Use the interactive Swagger UI at http://localhost:8000/docs to test endpoints manually.

## Architecture

```
backend/
├── __init__.py          # Package init
├── main.py              # FastAPI application and routes
├── config.py            # Configuration settings
├── models.py            # Pydantic models for request/response
├── sparql_client.py     # SPARQL query client
├── cache.py             # Caching layer
├── requirements.txt     # Python dependencies
├── tests/
│   ├── __init__.py
│   └── test_api.py      # Unit tests
└── README.md            # This file
```

## Development

### Code Style

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Adding New Endpoints

1. Define Pydantic models in `models.py`
2. Add SPARQL query to `sparql_client.py` `Queries` class
3. Create endpoint in `main.py`
4. Add unit tests in `tests/test_api.py`
5. Test using Swagger UI

### Example: Adding a New Endpoint

```python
# 1. Add model in models.py
class Device(BaseModel):
    name: str
    type: str

# 2. Add query in sparql_client.py
@staticmethod
def get_devices() -> str:
    return """
    SELECT ?name ?type WHERE {
      ?device a :PlasmaDevice ;
              :deviceName ?name .
    }
    """

# 3. Add endpoint in main.py
@app.get("/devices", response_model=List[Device])
async def list_devices(client: SPARQLClient = Depends(get_sparql_client)):
    query = Queries.get_devices()
    results = client.query(query)
    # ... process results ...
    return devices

# 4. Add test in tests/test_api.py
def test_list_devices():
    response = client.get("/devices")
    assert response.status_code == 200
```

## Performance

- **Caching**: 300-second TTL for query results
- **Connection Pooling**: Reuses SPARQL client connections
- **Async**: FastAPI async endpoints for better concurrency
- **Pagination**: Limits result sets to prevent memory issues

### Benchmarks

On typical hardware with Fuseki running locally:

- List papers: ~50ms
- Temperature query: ~100ms
- Statistics: ~150ms
- Cached responses: ~5ms

## Troubleshooting

### "Connection refused" to Fuseki

**Problem**: API can't connect to Fuseki

**Solution**:
```bash
# Check Fuseki is running
curl http://localhost:3030

# Start Fuseki
bash scripts/setup_fuseki.sh
```

### Import errors

**Problem**: ModuleNotFoundError

**Solution**:
```bash
# Ensure you're in the right directory
cd /path/to/askPhysics

# Install in development mode
pip install -e .
```

### Tests failing

**Problem**: Tests can't connect to Fuseki

**Solution**:
```bash
# Skip integration tests
pytest -m "not integration"

# Or start Fuseki first
bash scripts/setup_fuseki.sh
pytest
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use proper secrets management
2. **CORS**: Restrict allowed origins
3. **Rate Limiting**: Add rate limiting middleware
4. **Authentication**: Implement JWT authentication
5. **HTTPS**: Use reverse proxy (nginx, Traefik)
6. **Monitoring**: Add logging and metrics
7. **Caching**: Use Redis instead of in-memory cache
8. **Database**: Consider connection pooling

### Docker Deployment

```dockerfile
# Example Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t plasma-api .
docker run -p 8000:8000 plasma-api
```

## License

MIT

## Support

For issues and questions, see the main project README.
