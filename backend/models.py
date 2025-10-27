"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================
# Paper Models
# ============================================

class Paper(BaseModel):
    """Paper metadata."""
    arxiv_id: str = Field(..., description="arXiv identifier")
    title: str = Field(..., description="Paper title")
    authors: Optional[str] = Field(None, description="Comma-separated authors")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    publication_date: Optional[str] = Field(None, description="Publication date")
    pdf_url: Optional[str] = Field(None, description="URL to PDF")

    class Config:
        json_schema_extra = {
            "example": {
                "arxiv_id": "2310.12345",
                "title": "High confinement plasma experiments in DIII-D tokamak",
                "authors": "Smith, J., Doe, A., Johnson, B.",
                "abstract": "We report experimental results from...",
                "publication_date": "2023-10-15T00:00:00",
                "pdf_url": "https://arxiv.org/pdf/2310.12345.pdf"
            }
        }


class PaperList(BaseModel):
    """List of papers with pagination."""
    total: int = Field(..., description="Total number of papers")
    count: int = Field(..., description="Number of papers in this response")
    offset: int = Field(..., description="Offset for pagination")
    papers: List[Paper] = Field(..., description="List of papers")


# ============================================
# Measurement Models
# ============================================

class TemperatureMeasurement(BaseModel):
    """Temperature measurement from a paper."""
    arxiv_id: str = Field(..., description="arXiv ID of source paper")
    title: str = Field(..., description="Paper title")
    value: float = Field(..., description="Temperature value (original units)")
    unit: str = Field(..., description="Original unit (keV, eV, K)")
    normalized_value: float = Field(..., description="Normalized value in keV")
    confidence: str = Field(..., description="Extraction confidence (high/medium/low)")
    context: Optional[str] = Field(None, description="Extraction context")

    class Config:
        json_schema_extra = {
            "example": {
                "arxiv_id": "2310.12345",
                "title": "High confinement plasma experiments",
                "value": 5.2,
                "unit": "keV",
                "normalized_value": 5.2,
                "confidence": "high",
                "context": "...electron temperature Te = 5.2 keV sustained..."
            }
        }


class DensityMeasurement(BaseModel):
    """Density measurement from a paper."""
    arxiv_id: str = Field(..., description="arXiv ID of source paper")
    title: str = Field(..., description="Paper title")
    value: float = Field(..., description="Density value (original units)")
    unit: str = Field(..., description="Original unit (m^-3, cm^-3)")
    normalized_value: float = Field(..., description="Normalized value in m^-3")
    confidence: str = Field(..., description="Extraction confidence (high/medium/low)")
    context: Optional[str] = Field(None, description="Extraction context")

    class Config:
        json_schema_extra = {
            "example": {
                "arxiv_id": "2310.12345",
                "title": "High confinement plasma experiments",
                "value": 7.2e19,
                "unit": "m^-3",
                "normalized_value": 7.2e19,
                "confidence": "high",
                "context": "...electron density ne = 7.2 × 10^19 m^-3..."
            }
        }


class MeasurementList(BaseModel):
    """List of measurements."""
    total: int = Field(..., description="Total number of measurements")
    measurements: List[TemperatureMeasurement | DensityMeasurement]


# ============================================
# Statistics Models
# ============================================

class TemperatureStatistics(BaseModel):
    """Temperature statistics across all papers."""
    count: int = Field(..., description="Number of temperature measurements")
    avg_kev: Optional[float] = Field(None, description="Average temperature in keV")
    max_kev: Optional[float] = Field(None, description="Maximum temperature in keV")
    min_kev: Optional[float] = Field(None, description="Minimum temperature in keV")

    class Config:
        json_schema_extra = {
            "example": {
                "count": 24,
                "avg_kev": 6.5,
                "max_kev": 15.0,
                "min_kev": 0.003
            }
        }


class DensityStatistics(BaseModel):
    """Density statistics across all papers."""
    count: int = Field(..., description="Number of density measurements")
    avg_density: Optional[float] = Field(None, description="Average density in m^-3")
    max_density: Optional[float] = Field(None, description="Maximum density in m^-3")
    min_density: Optional[float] = Field(None, description="Minimum density in m^-3")

    class Config:
        json_schema_extra = {
            "example": {
                "count": 4,
                "avg_density": 5.5e19,
                "max_density": 8.9e19,
                "min_density": 4.0e19
            }
        }


class Statistics(BaseModel):
    """Overall statistics."""
    papers: int = Field(..., description="Total number of papers")
    temperature: TemperatureStatistics
    density: DensityStatistics


# ============================================
# Query Parameter Models
# ============================================

class TemperatureQuery(BaseModel):
    """Query parameters for temperature search."""
    min_temp: Optional[float] = Field(None, description="Minimum temperature in keV", ge=0)
    max_temp: Optional[float] = Field(None, description="Maximum temperature in keV", ge=0)
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "min_temp": 5.0,
                "max_temp": 15.0,
                "limit": 50
            }
        }


class DensityQuery(BaseModel):
    """Query parameters for density search."""
    min_density: Optional[float] = Field(None, description="Minimum density in m^-3", ge=0)
    max_density: Optional[float] = Field(None, description="Maximum density in m^-3", ge=0)
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "min_density": 1e19,
                "max_density": 1e20,
                "limit": 50
            }
        }


class SearchQuery(BaseModel):
    """Query parameters for paper search."""
    q: str = Field(..., description="Search term", min_length=1)
    limit: int = Field(20, description="Maximum number of results", ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "q": "tokamak",
                "limit": 10
            }
        }


# ============================================
# Response Models
# ============================================

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    fuseki_connected: bool = Field(..., description="Fuseki connection status")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "fuseki_connected": True,
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Query failed",
                "detail": "Connection to Fuseki timed out"
            }
        }
