"""
SPARQL client for querying the Fuseki triple store.
"""

import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Any, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)


class SPARQLClient:
    """Client for executing SPARQL queries against Fuseki."""

    def __init__(
        self,
        endpoint: str = None,
        username: str = None,
        password: str = None,
        timeout: int = None
    ):
        """
        Initialize SPARQL client.

        Args:
            endpoint: SPARQL endpoint URL
            username: Basic auth username
            password: Basic auth password
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint or settings.fuseki_endpoint
        self.username = username or settings.fuseki_username
        self.password = password or settings.fuseki_password
        self.timeout = timeout or settings.fuseki_timeout
        self.auth = HTTPBasicAuth(self.username, self.password) if self.username else None

        # Common prefixes
        self.prefixes = f"""
PREFIX : <{settings.plasma_namespace}>
PREFIX paper: <{settings.paper_namespace}>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

    def query(self, sparql: str, include_prefixes: bool = True) -> Dict[str, Any]:
        """
        Execute a SPARQL query.

        Args:
            sparql: SPARQL query string
            include_prefixes: Whether to prepend common prefixes

        Returns:
            Query results as dictionary

        Raises:
            Exception: If query fails
        """
        if include_prefixes:
            full_query = self.prefixes + "\n" + sparql
        else:
            full_query = sparql

        logger.debug(f"Executing SPARQL query: {full_query[:200]}...")

        try:
            response = requests.post(
                self.endpoint,
                data={'query': full_query},
                headers={'Accept': 'application/sparql-results+json'},
                auth=self.auth,
                timeout=self.timeout
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"SPARQL query failed: {e}")
            raise Exception(f"Failed to execute SPARQL query: {str(e)}")

    def get_bindings(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract bindings from SPARQL results.

        Args:
            results: Raw SPARQL results

        Returns:
            List of result bindings
        """
        if 'results' in results and 'bindings' in results['results']:
            return results['results']['bindings']
        return []

    def extract_values(self, bindings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract simple key-value pairs from bindings.

        Args:
            bindings: SPARQL bindings

        Returns:
            List of simplified result dictionaries
        """
        simplified = []
        for binding in bindings:
            row = {}
            for var, value_obj in binding.items():
                row[var] = value_obj.get('value')
            simplified.append(row)
        return simplified

    def count_query(self, sparql: str) -> int:
        """
        Execute a COUNT query and return the count.

        Args:
            sparql: SPARQL COUNT query

        Returns:
            Count value
        """
        results = self.query(sparql)
        bindings = self.get_bindings(results)
        if bindings and 'count' in bindings[0]:
            return int(bindings[0]['count']['value'])
        return 0

    def test_connection(self) -> bool:
        """
        Test connection to Fuseki endpoint.

        Returns:
            True if connection successful
        """
        try:
            query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
            self.query(query)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Queries module - predefined SPARQL queries
class Queries:
    """Collection of predefined SPARQL queries."""

    @staticmethod
    def list_papers(limit: int = 20, offset: int = 0) -> str:
        """List all papers with metadata."""
        return f"""
        SELECT ?arxivId ?title ?authors ?publicationDate
        WHERE {{
          ?paper a :Paper ;
                 :arxivId ?arxivId ;
                 :title ?title .
          OPTIONAL {{ ?paper :authors ?authors }}
          OPTIONAL {{ ?paper :publicationDate ?publicationDate }}
        }}
        ORDER BY DESC(?publicationDate)
        LIMIT {limit}
        OFFSET {offset}
        """

    @staticmethod
    def count_papers() -> str:
        """Count total papers."""
        return """
        SELECT (COUNT(DISTINCT ?paper) as ?count)
        WHERE {
          ?paper a :Paper .
        }
        """

    @staticmethod
    def get_paper_by_id(arxiv_id: str) -> str:
        """Get paper by arXiv ID."""
        return f"""
        SELECT ?title ?authors ?abstract ?publicationDate ?pdfUrl
        WHERE {{
          ?paper a :Paper ;
                 :arxivId "{arxiv_id}" ;
                 :title ?title .
          OPTIONAL {{ ?paper :authors ?authors }}
          OPTIONAL {{ ?paper :abstract ?abstract }}
          OPTIONAL {{ ?paper :publicationDate ?publicationDate }}
          OPTIONAL {{ ?paper :pdfUrl ?pdfUrl }}
        }}
        """

    @staticmethod
    def get_temperatures(
        min_temp: Optional[float] = None,
        max_temp: Optional[float] = None,
        limit: int = 100
    ) -> str:
        """Get temperature measurements with optional filtering."""
        filter_clause = ""
        if min_temp is not None or max_temp is not None:
            conditions = []
            if min_temp is not None:
                conditions.append(f"?normTemp >= {min_temp}")
            if max_temp is not None:
                conditions.append(f"?normTemp <= {max_temp}")
            filter_clause = "FILTER(" + " && ".join(conditions) + ")"

        return f"""
        SELECT ?arxivId ?title ?value ?unit ?normTemp ?confidence ?context
        WHERE {{
          ?paper a :Paper ;
                 :arxivId ?arxivId ;
                 :title ?title ;
                 :reports ?measurement .

          ?measurement :measuresParameter ?param ;
                       :confidence ?confidence .

          OPTIONAL {{ ?measurement :context ?context }}

          ?param a :Temperature ;
                 :value ?value ;
                 :unitString ?unit ;
                 :normalizedValue ?normTemp .

          {filter_clause}
        }}
        ORDER BY DESC(?normTemp)
        LIMIT {limit}
        """

    @staticmethod
    def get_densities(
        min_density: Optional[float] = None,
        max_density: Optional[float] = None,
        limit: int = 100
    ) -> str:
        """Get density measurements with optional filtering."""
        filter_clause = ""
        if min_density is not None or max_density is not None:
            conditions = []
            if min_density is not None:
                conditions.append(f"?normDens >= {min_density}")
            if max_density is not None:
                conditions.append(f"?normDens <= {max_density}")
            filter_clause = "FILTER(" + " && ".join(conditions) + ")"

        return f"""
        SELECT ?arxivId ?title ?value ?unit ?normDens ?confidence ?context
        WHERE {{
          ?paper a :Paper ;
                 :arxivId ?arxivId ;
                 :title ?title ;
                 :reports ?measurement .

          ?measurement :measuresParameter ?param ;
                       :confidence ?confidence .

          OPTIONAL {{ ?measurement :context ?context }}

          ?param a :Density ;
                 :value ?value ;
                 :unitString ?unit ;
                 :normalizedValue ?normDens .

          {filter_clause}
        }}
        ORDER BY DESC(?normDens)
        LIMIT {limit}
        """

    @staticmethod
    def temperature_statistics() -> str:
        """Get temperature statistics."""
        return """
        SELECT
          (COUNT(?temp) as ?count)
          (ROUND(AVG(?normValue) * 100) / 100 as ?avgKeV)
          (ROUND(MAX(?normValue) * 100) / 100 as ?maxKeV)
          (ROUND(MIN(?normValue) * 100) / 100 as ?minKeV)
        WHERE {
          ?temp a :Temperature ;
                :normalizedValue ?normValue .
        }
        """

    @staticmethod
    def density_statistics() -> str:
        """Get density statistics."""
        return """
        SELECT
          (COUNT(?dens) as ?count)
          (AVG(?normValue) as ?avgDensity)
          (MAX(?normValue) as ?maxDensity)
          (MIN(?normValue) as ?minDensity)
        WHERE {
          ?dens a :Density ;
                :normalizedValue ?normValue .
        }
        """

    @staticmethod
    def papers_with_both_params() -> str:
        """Find papers with both temperature and density measurements."""
        return """
        SELECT DISTINCT ?arxivId ?title
        WHERE {
          ?paper a :Paper ;
                 :arxivId ?arxivId ;
                 :title ?title ;
                 :reports ?meas1 ;
                 :reports ?meas2 .

          ?meas1 :measuresParameter ?temp .
          ?temp a :Temperature .

          ?meas2 :measuresParameter ?dens .
          ?dens a :Density .
        }
        """

    @staticmethod
    def search_papers(search_term: str, limit: int = 20) -> str:
        """Search papers by title or abstract."""
        return f"""
        SELECT DISTINCT ?arxivId ?title ?authors
        WHERE {{
          ?paper a :Paper ;
                 :arxivId ?arxivId ;
                 :title ?title .
          OPTIONAL {{ ?paper :authors ?authors }}
          OPTIONAL {{ ?paper :abstract ?abstract }}

          FILTER(
            REGEX(?title, "{search_term}", "i") ||
            REGEX(?abstract, "{search_term}", "i")
          )
        }}
        LIMIT {limit}
        """
