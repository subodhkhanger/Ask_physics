"""
Dynamic SPARQL Query Builder.

Constructs SPARQL queries from parsed natural language queries.
"""

from typing import Optional, List
from datetime import datetime, timedelta

try:
    from .nlp_query_processor import ParsedQuery, ParameterRange
except ImportError:
    from nlp_query_processor import ParsedQuery, ParameterRange


class DynamicSPARQLBuilder:
    """
    Builds SPARQL queries dynamically based on parsed query parameters.
    """

    PREFIX = """PREFIX : <http://example.org/plasma#>
PREFIX paper: <http://example.org/plasma/paper/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

    def build_search_query(self, parsed: ParsedQuery, limit: int = 20) -> str:
        """
        Build a search query based on parsed parameters.

        Args:
            parsed: ParsedQuery object with extracted parameters
            limit: Maximum number of results

        Returns:
            SPARQL query string
        """
        # Base SELECT clause
        select_vars = ["?paper", "?title", "?authors", "?publicationDate"]

        # Add temperature vars if filtering by temperature
        if "temperature" in parsed.parameters:
            select_vars.extend(["?tempValue", "?tempUnit", "?tempNormalized"])

        # Add density vars if filtering by density
        if "density" in parsed.parameters:
            select_vars.extend(["?densValue", "?densUnit", "?densNormalized"])

        query = f"{self.PREFIX}\n"
        query += f"SELECT DISTINCT {' '.join(select_vars)}\n"
        query += "WHERE {\n"
        query += "  ?paper a :Paper ;\n"
        query += "         :title ?title .\n"
        query += "  OPTIONAL { ?paper :authors ?authors }\n"
        query += "  OPTIONAL { ?paper :publicationDate ?publicationDate }\n\n"

        # Add temperature filter
        if "temperature" in parsed.parameters:
            query += self._build_temperature_filter(parsed.parameters["temperature"])

        # Add density filter
        if "density" in parsed.parameters:
            query += self._build_density_filter(parsed.parameters["density"])

        # Add temporal filter
        if parsed.temporal_constraint:
            query += self._build_temporal_filter(parsed.temporal_constraint)

        # Add keyword filter
        if parsed.keywords:
            query += self._build_keyword_filter(parsed.keywords)

        query += "}\n"
        # Only order by publication date if it exists, otherwise order by title
        if parsed.temporal_constraint:
            query += "ORDER BY DESC(?publicationDate)\n"
        else:
            query += "ORDER BY ?title\n"
        query += f"LIMIT {limit}"

        return query

    def _build_temperature_filter(self, temp_range: ParameterRange) -> str:
        """Build temperature filter clause."""
        filter_clause = """  # Temperature filter
  ?paper :reports ?tempMeas .
  ?tempMeas :measuresParameter ?temp .
  ?temp a :Temperature ;
        :value ?tempValue ;
        :unitString ?tempUnit ;
        :normalizedValue ?tempNormalized .
"""

        filters = []
        if temp_range.normalized_min is not None:
            filters.append(f"?tempNormalized >= {temp_range.normalized_min}")
        if temp_range.normalized_max is not None:
            filters.append(f"?tempNormalized <= {temp_range.normalized_max}")

        if filters:
            filter_clause += f"  FILTER({' && '.join(filters)})\n"

        return filter_clause + "\n"

    def _build_density_filter(self, dens_range: ParameterRange) -> str:
        """Build density filter clause."""
        filter_clause = """  # Density filter
  ?paper :reports ?densMeas .
  ?densMeas :measuresParameter ?dens .
  ?dens a :Density ;
        :value ?densValue ;
        :unitString ?densUnit ;
        :normalizedValue ?densNormalized .
"""

        filters = []
        if dens_range.normalized_min is not None:
            filters.append(f"?densNormalized >= {dens_range.normalized_min}")
        if dens_range.normalized_max is not None:
            filters.append(f"?densNormalized <= {dens_range.normalized_max}")

        if filters:
            filter_clause += f"  FILTER({' && '.join(filters)})\n"

        return filter_clause + "\n"

    def _build_temporal_filter(self, temporal: str) -> str:
        """Build temporal filter clause."""
        if temporal == "recent":
            # Recent = last 2 years
            cutoff_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
            return f'  FILTER(?publicationDate >= "{cutoff_date}"^^xsd:date)\n\n'
        elif temporal.isdigit() and len(temporal) == 4:
            # Specific year
            return f'  FILTER(YEAR(?publicationDate) = {temporal})\n\n'
        return ""

    def _build_keyword_filter(self, keywords: List[str]) -> str:
        """Build keyword filter clause (searches in title and abstract)."""
        if not keywords:
            return ""

        # Create regex pattern for all keywords (OR logic)
        pattern = "|".join(keywords)
        return f'  FILTER(REGEX(?title, "{pattern}", "i"))\n\n'

    def build_statistics_query(self, parsed: ParsedQuery) -> str:
        """Build statistics query."""
        query = f"{self.PREFIX}\n"

        if "temperature" in parsed.parameters:
            query += """SELECT
  (COUNT(?temp) as ?count)
  (AVG(?normValue) as ?avgKeV)
  (MAX(?normValue) as ?maxKeV)
  (MIN(?normValue) as ?minKeV)
WHERE {
  ?temp a :Temperature ;
        :normalizedValue ?normValue .
"""
            temp_range = parsed.parameters["temperature"]
            filters = []
            if temp_range.normalized_min:
                filters.append(f"?normValue >= {temp_range.normalized_min}")
            if temp_range.normalized_max:
                filters.append(f"?normValue <= {temp_range.normalized_max}")

            if filters:
                query += f"  FILTER({' && '.join(filters)})\n"
            query += "}"

        elif "density" in parsed.parameters:
            query += """SELECT
  (COUNT(?dens) as ?count)
  (AVG(?normValue) as ?avgDensity)
  (MAX(?normValue) as ?maxDensity)
  (MIN(?normValue) as ?minDensity)
WHERE {
  ?dens a :Density ;
        :normalizedValue ?normValue .
"""
            dens_range = parsed.parameters["density"]
            filters = []
            if dens_range.normalized_min:
                filters.append(f"?normValue >= {dens_range.normalized_min}")
            if dens_range.normalized_max:
                filters.append(f"?normValue <= {dens_range.normalized_max}")

            if filters:
                query += f"  FILTER({' && '.join(filters)})\n"
            query += "}"

        return query


# Example usage
if __name__ == "__main__":
    from nlp_query_processor import NLPQueryProcessor

    processor = NLPQueryProcessor()
    builder = DynamicSPARQLBuilder()

    test_query = "Show me recent research on electron density between 10^16 and 10^18 m^-3"
    parsed = processor.parse(test_query)

    print("Natural Language Query:")
    print(test_query)
    print("\nParsed Parameters:")
    print(parsed.model_dump_json(indent=2))
    print("\nGenerated SPARQL:")
    print(builder.build_search_query(parsed))
