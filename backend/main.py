"""
FastAPI application for Plasma Physics Literature Search.

This API provides REST endpoints for querying plasma physics experimental
parameters extracted from scientific literature and stored in an RDF knowledge graph.
"""

from fastapi import FastAPI, HTTPException, Query as QueryParam, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from .config import settings
from .sparql_client import SPARQLClient, Queries
from .models import (
    Paper, PaperList, TemperatureMeasurement, DensityMeasurement,
    TemperatureStatistics, DensityStatistics, Statistics,
    HealthCheck, ErrorResponse
)
from .cache import cache_response

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Initialize SPARQL client
sparql_client = SPARQLClient()


# ============================================
# Dependency Injection
# ============================================

def get_sparql_client() -> SPARQLClient:
    """Get SPARQL client instance."""
    return sparql_client


# ============================================
# Health Check
# ============================================

@app.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """Check API and Fuseki connection status."""
    fuseki_ok = sparql_client.test_connection()
    return HealthCheck(
        status="ok" if fuseki_ok else "degraded",
        fuseki_connected=fuseki_ok,
        version=settings.app_version
    )


# ============================================
# Paper Endpoints
# ============================================

@app.get(
    "/papers",
    response_model=PaperList,
    tags=["Papers"],
    summary="List all papers"
)
@cache_response(ttl=300)
async def list_papers(
    limit: int = QueryParam(20, ge=1, le=100, description="Number of papers to return"),
    offset: int = QueryParam(0, ge=0, description="Offset for pagination"),
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    List all papers with metadata.

    - **limit**: Number of papers per page (1-100)
    - **offset**: Pagination offset

    Returns paper metadata including arXiv ID, title, authors, and publication date.
    """
    try:
        # Get total count
        count_query = Queries.count_papers()
        total = client.count_query(count_query)

        # Get papers
        papers_query = Queries.list_papers(limit=limit, offset=offset)
        results = client.query(papers_query)
        bindings = client.get_bindings(results)

        papers = []
        for binding in bindings:
            paper = Paper(
                arxiv_id=binding.get('arxivId', {}).get('value', ''),
                title=binding.get('title', {}).get('value', ''),
                authors=binding.get('authors', {}).get('value'),
                publication_date=binding.get('publicationDate', {}).get('value')
            )
            papers.append(paper)

        return PaperList(total=total, count=len(papers), offset=offset, papers=papers)

    except Exception as e:
        logger.error(f"Failed to list papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/papers/{arxiv_id}",
    response_model=Paper,
    tags=["Papers"],
    summary="Get paper by arXiv ID"
)
@cache_response(ttl=600)
async def get_paper(
    arxiv_id: str,
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get detailed information about a specific paper.

    - **arxiv_id**: arXiv identifier (e.g., "2310.12345")

    Returns full paper metadata including abstract and PDF URL.
    """
    try:
        query = Queries.get_paper_by_id(arxiv_id)
        results = client.query(query)
        bindings = client.get_bindings(results)

        if not bindings:
            raise HTTPException(status_code=404, detail=f"Paper {arxiv_id} not found")

        binding = bindings[0]
        paper = Paper(
            arxiv_id=arxiv_id,
            title=binding.get('title', {}).get('value', ''),
            authors=binding.get('authors', {}).get('value'),
            abstract=binding.get('abstract', {}).get('value'),
            publication_date=binding.get('publicationDate', {}).get('value'),
            pdf_url=binding.get('pdfUrl', {}).get('value')
        )
        return paper

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get paper {arxiv_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/papers/search",
    response_model=List[Paper],
    tags=["Papers"],
    summary="Search papers"
)
@cache_response(ttl=300)
async def search_papers(
    q: str = QueryParam(..., min_length=1, description="Search query"),
    limit: int = QueryParam(20, ge=1, le=100, description="Maximum results"),
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Search papers by title or abstract.

    - **q**: Search term (searches in title and abstract)
    - **limit**: Maximum number of results

    Returns papers matching the search term.
    """
    try:
        query = Queries.search_papers(q, limit=limit)
        results = client.query(query)
        bindings = client.get_bindings(results)

        papers = []
        for binding in bindings:
            paper = Paper(
                arxiv_id=binding.get('arxivId', {}).get('value', ''),
                title=binding.get('title', {}).get('value', ''),
                authors=binding.get('authors', {}).get('value')
            )
            papers.append(paper)

        return papers

    except Exception as e:
        logger.error(f"Search failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Temperature Endpoints
# ============================================

@app.get(
    "/temperatures",
    response_model=List[TemperatureMeasurement],
    tags=["Measurements"],
    summary="Get temperature measurements"
)
@cache_response(ttl=300)
async def get_temperatures(
    min_temp: Optional[float] = QueryParam(None, ge=0, description="Minimum temperature in keV"),
    max_temp: Optional[float] = QueryParam(None, ge=0, description="Maximum temperature in keV"),
    limit: int = QueryParam(100, ge=1, le=1000, description="Maximum results"),
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get temperature measurements with optional filtering.

    - **min_temp**: Minimum temperature in keV (inclusive)
    - **max_temp**: Maximum temperature in keV (inclusive)
    - **limit**: Maximum number of results

    Returns temperature measurements with normalized values in keV.
    """
    try:
        query = Queries.get_temperatures(min_temp=min_temp, max_temp=max_temp, limit=limit)
        results = client.query(query)
        bindings = client.get_bindings(results)

        measurements = []
        for binding in bindings:
            measurement = TemperatureMeasurement(
                arxiv_id=binding.get('arxivId', {}).get('value', ''),
                title=binding.get('title', {}).get('value', ''),
                value=float(binding.get('value', {}).get('value', 0)),
                unit=binding.get('unit', {}).get('value', ''),
                normalized_value=float(binding.get('normTemp', {}).get('value', 0)),
                confidence=binding.get('confidence', {}).get('value', 'unknown'),
                context=binding.get('context', {}).get('value')
            )
            measurements.append(measurement)

        return measurements

    except Exception as e:
        logger.error(f"Failed to get temperatures: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/temperatures/statistics",
    response_model=TemperatureStatistics,
    tags=["Statistics"],
    summary="Get temperature statistics"
)
@cache_response(ttl=300)
async def temperature_statistics(
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get aggregated statistics for all temperature measurements.

    Returns count, average, maximum, and minimum temperatures in keV.
    """
    try:
        query = Queries.temperature_statistics()
        results = client.query(query)
        bindings = client.get_bindings(results)

        if not bindings:
            return TemperatureStatistics(count=0, avg_kev=None, max_kev=None, min_kev=None)

        binding = bindings[0]
        stats = TemperatureStatistics(
            count=int(binding.get('count', {}).get('value', 0)),
            avg_kev=float(binding.get('avgKeV', {}).get('value', 0)) if 'avgKeV' in binding else None,
            max_kev=float(binding.get('maxKeV', {}).get('value', 0)) if 'maxKeV' in binding else None,
            min_kev=float(binding.get('minKeV', {}).get('value', 0)) if 'minKeV' in binding else None
        )
        return stats

    except Exception as e:
        logger.error(f"Failed to get temperature statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Density Endpoints
# ============================================

@app.get(
    "/densities",
    response_model=List[DensityMeasurement],
    tags=["Measurements"],
    summary="Get density measurements"
)
@cache_response(ttl=300)
async def get_densities(
    min_density: Optional[float] = QueryParam(None, ge=0, description="Minimum density in m^-3"),
    max_density: Optional[float] = QueryParam(None, ge=0, description="Maximum density in m^-3"),
    limit: int = QueryParam(100, ge=1, le=1000, description="Maximum results"),
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get density measurements with optional filtering.

    - **min_density**: Minimum density in m^-3 (inclusive)
    - **max_density**: Maximum density in m^-3 (inclusive)
    - **limit**: Maximum number of results

    Returns density measurements with normalized values in m^-3.
    """
    try:
        query = Queries.get_densities(min_density=min_density, max_density=max_density, limit=limit)
        results = client.query(query)
        bindings = client.get_bindings(results)

        measurements = []
        for binding in bindings:
            measurement = DensityMeasurement(
                arxiv_id=binding.get('arxivId', {}).get('value', ''),
                title=binding.get('title', {}).get('value', ''),
                value=float(binding.get('value', {}).get('value', 0)),
                unit=binding.get('unit', {}).get('value', ''),
                normalized_value=float(binding.get('normDens', {}).get('value', 0)),
                confidence=binding.get('confidence', {}).get('value', 'unknown'),
                context=binding.get('context', {}).get('value')
            )
            measurements.append(measurement)

        return measurements

    except Exception as e:
        logger.error(f"Failed to get densities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/densities/statistics",
    response_model=DensityStatistics,
    tags=["Statistics"],
    summary="Get density statistics"
)
@cache_response(ttl=300)
async def density_statistics(
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get aggregated statistics for all density measurements.

    Returns count, average, maximum, and minimum densities in m^-3.
    """
    try:
        query = Queries.density_statistics()
        results = client.query(query)
        bindings = client.get_bindings(results)

        if not bindings:
            return DensityStatistics(count=0, avg_density=None, max_density=None, min_density=None)

        binding = bindings[0]
        stats = DensityStatistics(
            count=int(binding.get('count', {}).get('value', 0)),
            avg_density=float(binding.get('avgDensity', {}).get('value', 0)) if 'avgDensity' in binding else None,
            max_density=float(binding.get('maxDensity', {}).get('value', 0)) if 'maxDensity' in binding else None,
            min_density=float(binding.get('minDensity', {}).get('value', 0)) if 'minDensity' in binding else None
        )
        return stats

    except Exception as e:
        logger.error(f"Failed to get density statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Combined Statistics
# ============================================

@app.get(
    "/statistics",
    response_model=Statistics,
    tags=["Statistics"],
    summary="Get overall statistics"
)
@cache_response(ttl=300)
async def get_statistics(
    client: SPARQLClient = Depends(get_sparql_client)
):
    """
    Get overall statistics for the knowledge graph.

    Returns statistics for papers, temperatures, and densities.
    """
    try:
        # Get paper count
        paper_count = client.count_query(Queries.count_papers())

        # Get temperature stats
        temp_query = Queries.temperature_statistics()
        temp_results = client.query(temp_query)
        temp_bindings = client.get_bindings(temp_results)

        if temp_bindings:
            temp_binding = temp_bindings[0]
            temp_stats = TemperatureStatistics(
                count=int(temp_binding.get('count', {}).get('value', 0)),
                avg_kev=float(temp_binding.get('avgKeV', {}).get('value', 0)) if 'avgKeV' in temp_binding else None,
                max_kev=float(temp_binding.get('maxKeV', {}).get('value', 0)) if 'maxKeV' in temp_binding else None,
                min_kev=float(temp_binding.get('minKeV', {}).get('value', 0)) if 'minKeV' in temp_binding else None
            )
        else:
            temp_stats = TemperatureStatistics(count=0, avg_kev=None, max_kev=None, min_kev=None)

        # Get density stats
        dens_query = Queries.density_statistics()
        dens_results = client.query(dens_query)
        dens_bindings = client.get_bindings(dens_results)

        if dens_bindings:
            dens_binding = dens_bindings[0]
            dens_stats = DensityStatistics(
                count=int(dens_binding.get('count', {}).get('value', 0)),
                avg_density=float(dens_binding.get('avgDensity', {}).get('value', 0)) if 'avgDensity' in dens_binding else None,
                max_density=float(dens_binding.get('maxDensity', {}).get('value', 0)) if 'maxDensity' in dens_binding else None,
                min_density=float(dens_binding.get('minDensity', {}).get('value', 0)) if 'minDensity' in dens_binding else None
            )
        else:
            dens_stats = DensityStatistics(count=0, avg_density=None, max_density=None, min_density=None)

        return Statistics(
            papers=paper_count,
            temperature=temp_stats,
            density=dens_stats
        )

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Fuseki endpoint: {settings.fuseki_endpoint}")

    # Test connection
    if sparql_client.test_connection():
        logger.info("✓ Connected to Fuseki")
    else:
        logger.warning("✗ Failed to connect to Fuseki - some endpoints may not work")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
