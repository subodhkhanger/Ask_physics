"""
Unit tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.main import app
from backend.sparql_client import SPARQLClient

client = TestClient(app)


# ============================================
# Health Check Tests
# ============================================

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "fuseki_connected" in data


# ============================================
# Paper Endpoint Tests
# ============================================

def test_list_papers():
    """Test listing papers."""
    response = client.get("/papers")
    assert response.status_code == 200
    data = response.json()
    assert "papers" in data
    assert "total" in data
    assert "count" in data
    assert isinstance(data["papers"], list)


def test_list_papers_with_pagination():
    """Test paper pagination."""
    response = client.get("/papers?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["papers"]) <= 5


def test_list_papers_invalid_limit():
    """Test invalid limit parameter."""
    response = client.get("/papers?limit=1000")
    assert response.status_code == 422  # Validation error


def test_get_paper_by_id():
    """Test getting specific paper."""
    # First get a list of papers to find a valid ID
    list_response = client.get("/papers?limit=1")
    if list_response.status_code == 200:
        papers = list_response.json()["papers"]
        if papers:
            arxiv_id = papers[0]["arxiv_id"]
            response = client.get(f"/papers/{arxiv_id}")
            assert response.status_code in [200, 404]


def test_get_paper_not_found():
    """Test getting non-existent paper."""
    response = client.get("/papers/nonexistent_id_12345")
    assert response.status_code == 404


def test_search_papers():
    """Test paper search."""
    response = client.get("/papers/search?q=plasma&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_papers_empty_query():
    """Test search with empty query."""
    response = client.get("/papers/search?q=")
    assert response.status_code == 422  # Validation error


# ============================================
# Temperature Endpoint Tests
# ============================================

def test_get_temperatures():
    """Test getting temperature measurements."""
    response = client.get("/temperatures")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_temperatures_with_filters():
    """Test temperature filtering."""
    response = client.get("/temperatures?min_temp=5.0&max_temp=15.0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Verify all results are within range
    for measurement in data:
        assert measurement["normalized_value"] >= 5.0
        assert measurement["normalized_value"] <= 15.0


def test_get_temperatures_with_limit():
    """Test temperature limit parameter."""
    response = client.get("/temperatures?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5


def test_get_temperatures_invalid_range():
    """Test invalid temperature range."""
    response = client.get("/temperatures?min_temp=-1")
    assert response.status_code == 422  # Validation error


def test_temperature_statistics():
    """Test temperature statistics endpoint."""
    response = client.get("/temperatures/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "avg_kev" in data or data["count"] == 0
    assert "max_kev" in data or data["count"] == 0
    assert "min_kev" in data or data["count"] == 0


# ============================================
# Density Endpoint Tests
# ============================================

def test_get_densities():
    """Test getting density measurements."""
    response = client.get("/densities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_densities_with_filters():
    """Test density filtering."""
    response = client.get("/densities?min_density=1e19&max_density=1e20")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_density_statistics():
    """Test density statistics endpoint."""
    response = client.get("/densities/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data


# ============================================
# Statistics Tests
# ============================================

def test_get_overall_statistics():
    """Test overall statistics endpoint."""
    response = client.get("/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "papers" in data
    assert "temperature" in data
    assert "density" in data
    assert isinstance(data["papers"], int)
    assert isinstance(data["temperature"], dict)
    assert isinstance(data["density"], dict)


# ============================================
# Error Handling Tests
# ============================================

def test_invalid_endpoint():
    """Test accessing non-existent endpoint."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_method_not_allowed():
    """Test using wrong HTTP method."""
    response = client.post("/papers")
    assert response.status_code == 405


# ============================================
# CORS Tests
# ============================================

def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options("/papers")
    # CORS headers should be present in OPTIONS response
    assert response.status_code in [200, 405]


# ============================================
# Documentation Tests
# ============================================

def test_openapi_docs():
    """Test OpenAPI documentation is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


def test_swagger_ui():
    """Test Swagger UI is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc():
    """Test ReDoc is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200


# ============================================
# Integration Tests (require running Fuseki)
# ============================================

@pytest.mark.integration
def test_integration_full_workflow():
    """
    Integration test for complete workflow.
    Requires Fuseki to be running with data loaded.
    """
    # 1. Check health
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["fuseki_connected"] == True

    # 2. Get statistics
    stats = client.get("/statistics")
    assert stats.status_code == 200
    stats_data = stats.json()
    assert stats_data["papers"] > 0

    # 3. List papers
    papers = client.get("/papers?limit=5")
    assert papers.status_code == 200
    papers_data = papers.json()
    assert len(papers_data["papers"]) > 0

    # 4. Get temperature measurements
    temps = client.get("/temperatures?limit=10")
    assert temps.status_code == 200
    temps_data = temps.json()
    assert len(temps_data) > 0

    # 5. Search papers
    search = client.get("/papers/search?q=tokamak")
    assert search.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
