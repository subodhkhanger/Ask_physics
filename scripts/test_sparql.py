#!/usr/bin/env python3
"""
Test SPARQL queries against the Fuseki triple store.

This script demonstrates querying the plasma physics knowledge graph
using SPARQL queries programmatically.

Usage:
    # Test against local Fuseki
    python scripts/test_sparql.py --endpoint http://localhost:3030/plasma/query

    # Test against file directly (using rdflib)
    python scripts/test_sparql.py --file data/plasma_data.ttl
"""

import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Dict, List, Any


class SPARQLTester:
    """Test SPARQL queries against Fuseki endpoint or local file."""

    def __init__(self, endpoint: str = None, username: str = "admin", password: str = "admin123"):
        self.endpoint = endpoint
        self.auth = HTTPBasicAuth(username, password) if username else None

        self.prefixes = """
PREFIX : <http://example.org/plasma#>
PREFIX paper: <http://example.org/plasma/paper/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

    def query(self, sparql: str) -> Dict[str, Any]:
        """Execute a SPARQL query against the endpoint."""
        if not self.endpoint:
            raise ValueError("No endpoint configured")

        full_query = self.prefixes + "\n" + sparql

        response = requests.post(
            self.endpoint,
            data={'query': full_query},
            headers={'Accept': 'application/sparql-results+json'},
            auth=self.auth,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Query failed with status {response.status_code}: {response.text}")

        return response.json()

    def format_results(self, results: Dict[str, Any]) -> str:
        """Format SPARQL results for display."""
        if 'results' not in results or 'bindings' not in results['results']:
            return "No results"

        bindings = results['results']['bindings']
        if not bindings:
            return "No results found"

        # Get column names
        vars = results['head']['vars']

        # Format as table
        lines = []
        lines.append(" | ".join(vars))
        lines.append("-" * (len(" | ".join(vars))))

        for binding in bindings[:10]:  # Limit to 10 rows
            row = []
            for var in vars:
                if var in binding:
                    value = binding[var]['value']
                    # Truncate long values
                    if len(str(value)) > 50:
                        value = str(value)[:47] + "..."
                    row.append(str(value))
                else:
                    row.append("")
            lines.append(" | ".join(row))

        if len(bindings) > 10:
            lines.append(f"... ({len(bindings) - 10} more rows)")

        return "\n".join(lines)


def test_basic_queries(tester: SPARQLTester):
    """Run a set of basic test queries."""

    print("=" * 80)
    print("SPARQL Query Tests - Plasma Physics Knowledge Graph")
    print("=" * 80)
    print()

    # Query 1: Count papers
    print("Query 1: Count total papers")
    print("-" * 80)
    query1 = """
    SELECT (COUNT(DISTINCT ?paper) as ?count)
    WHERE {
      ?paper a :Paper .
    }
    """
    try:
        results = tester.query(query1)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Query 2: List papers with titles
    print("Query 2: List papers with titles")
    print("-" * 80)
    query2 = """
    SELECT ?title ?authors
    WHERE {
      ?paper a :Paper ;
             :title ?title ;
             :authors ?authors .
    }
    LIMIT 5
    """
    try:
        results = tester.query(query2)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Query 3: Temperature statistics
    print("Query 3: Temperature statistics (normalized to keV)")
    print("-" * 80)
    query3 = """
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
    try:
        results = tester.query(query3)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Query 4: High temperature papers
    print("Query 4: Papers with high temperature (> 10 keV)")
    print("-" * 80)
    query4 = """
    SELECT DISTINCT ?title ?value ?unit
    WHERE {
      ?paper a :Paper ;
             :title ?title ;
             :reports ?measurement .

      ?measurement :measuresParameter ?param .

      ?param a :Temperature ;
             :value ?value ;
             :unitString ?unit ;
             :normalizedValue ?normTemp .

      FILTER(?normTemp > 10)
    }
    ORDER BY DESC(?normTemp)
    LIMIT 5
    """
    try:
        results = tester.query(query4)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Query 5: Papers with both temp and density
    print("Query 5: Papers with both temperature and density measurements")
    print("-" * 80)
    query5 = """
    SELECT DISTINCT ?title
    WHERE {
      ?paper a :Paper ;
             :title ?title ;
             :reports ?meas1 ;
             :reports ?meas2 .

      ?meas1 :measuresParameter ?temp .
      ?temp a :Temperature .

      ?meas2 :measuresParameter ?dens .
      ?dens a :Density .
    }
    """
    try:
        results = tester.query(query5)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    # Query 6: Measurement confidence distribution
    print("Query 6: Measurement confidence distribution")
    print("-" * 80)
    query6 = """
    SELECT ?confidence (COUNT(?measurement) as ?count)
    WHERE {
      ?measurement a :Measurement ;
                   :confidence ?confidence .
    }
    GROUP BY ?confidence
    ORDER BY DESC(?count)
    """
    try:
        results = tester.query(query6)
        print(tester.format_results(results))
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

    print("=" * 80)
    print("Test complete!")
    print("=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test SPARQL queries against Fuseki'
    )
    parser.add_argument(
        '--endpoint',
        type=str,
        default='http://localhost:3030/plasma/query',
        help='SPARQL endpoint URL'
    )
    parser.add_argument(
        '--username',
        type=str,
        default='admin',
        help='Fuseki username'
    )
    parser.add_argument(
        '--password',
        type=str,
        default='admin123',
        help='Fuseki password'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Test against local TTL file using rdflib (not implemented yet)'
    )

    args = parser.parse_args()

    if args.file:
        print("File-based testing not yet implemented. Use --endpoint instead.")
        return

    # Create tester and run queries
    tester = SPARQLTester(
        endpoint=args.endpoint,
        username=args.username,
        password=args.password
    )

    # Test connection
    print(f"Testing connection to {args.endpoint}...")
    try:
        results = tester.query("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
        print("✓ Connection successful")
        print()
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print()
        print("Make sure Fuseki is running:")
        print("  bash scripts/setup_fuseki.sh")
        return

    # Run test queries
    test_basic_queries(tester)


if __name__ == '__main__':
    main()
