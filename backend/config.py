"""
Configuration for the Plasma Physics API.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """API settings loaded from environment variables."""

    # API Metadata
    app_name: str = "Plasma Physics Literature Search API"
    app_version: str = "1.0.0"
    app_description: str = "REST API for querying plasma physics experimental parameters from scientific literature"

    # Fuseki Configuration
    fuseki_endpoint: str = "http://localhost:3030/plasma/query"
    fuseki_update_endpoint: str = "http://localhost:3030/plasma/update"
    fuseki_data_endpoint: str = "http://localhost:3030/plasma/data"
    fuseki_username: str = "admin"
    fuseki_password: str = "admin123"

    # RDF Configuration
    plasma_namespace: str = "http://example.org/plasma#"
    paper_namespace: str = "http://example.org/plasma/paper/"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    debug: bool = True

    # CORS Configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:8501"]  # Frontend URLs
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # Caching Configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Query Limits
    max_results: int = 1000
    default_page_size: int = 20

    # Timeout
    fuseki_timeout: int = 30  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env file


# Global settings instance
settings = Settings()
