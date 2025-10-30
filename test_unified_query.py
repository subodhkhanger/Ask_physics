#!/usr/bin/env python3
"""
Test script for Unified Natural Language Query Flow

Tests the complete pipeline:
1. Natural language query parsing
2. SPARQL generation
3. Query execution (if Fuseki is running)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.nlp_query_processor import NLPQueryProcessor
from backend.query_builder import DynamicSPARQLBuilder


def test_query_parsing():
    """Test NLP query parsing."""
    print("=" * 70)
    print("TEST 1: Natural Language Query Parsing")
    print("=" * 70)

    processor = NLPQueryProcessor()

    test_queries = [
        "Show me recent research on electron density between 10^16 and 10^18 m^-3",
        "Find papers with temperature above 10 keV",
        "Recent tokamak experiments",
        "Papers with both high temperature and high density",
        "Low temperature plasmas from 2023",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        print("-" * 70)

        try:
            parsed = processor.parse(query)

            print(f"   Intent: {parsed.intent}")
            print(f"   Confidence: {parsed.confidence:.2f}")

            if parsed.parameters:
                print("   Parameters:")
                for param_name, param_range in parsed.parameters.items():
                    print(f"     - {param_name}:")
                    if param_range.min_value:
                        print(f"       Min: {param_range.min_value} {param_range.unit} "
                              f"(normalized: {param_range.normalized_min})")
                    if param_range.max_value:
                        print(f"       Max: {param_range.max_value} {param_range.unit} "
                              f"(normalized: {param_range.normalized_max})")

            if parsed.keywords:
                print(f"   Keywords: {', '.join(parsed.keywords)}")

            if parsed.temporal_constraint:
                print(f"   Time constraint: {parsed.temporal_constraint}")

            print("   ✓ PASS")

        except Exception as e:
            print(f"   ✗ FAIL: {e}")
            import traceback
            traceback.print_exc()


def test_sparql_generation():
    """Test SPARQL query generation."""
    print("\n" + "=" * 70)
    print("TEST 2: SPARQL Query Generation")
    print("=" * 70)

    processor = NLPQueryProcessor()
    builder = DynamicSPARQLBuilder()

    test_query = "Show me recent research on electron density between 10^16 and 10^18 m^-3"

    print(f"\nQuery: \"{test_query}\"")
    print("-" * 70)

    try:
        parsed = processor.parse(test_query)
        sparql = builder.build_search_query(parsed, limit=10)

        print("\nGenerated SPARQL Query:")
        print(sparql)
        print("\n✓ PASS")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()


def test_api_endpoint():
    """Test the API endpoint (requires running backend)."""
    print("\n" + "=" * 70)
    print("TEST 3: API Endpoint Test")
    print("=" * 70)

    try:
        import requests

        api_url = "http://localhost:8000"

        # Check if backend is running
        try:
            health_response = requests.get(f"{api_url}/health", timeout=2)
            print(f"\n✓ Backend is running (status: {health_response.json().get('status')})")
        except requests.exceptions.ConnectionError:
            print("\n⚠ Backend is not running. Start it with:")
            print("  cd backend && python run.py")
            return

        # Test query endpoint
        test_query = "Find papers with temperature above 5 keV"
        print(f"\nTesting query: \"{test_query}\"")
        print("-" * 70)

        response = requests.post(
            f"{api_url}/query/natural-language",
            json={
                "query": test_query,
                "limit": 5,
                "include_sparql": True
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Query successful!")
            print(f"  - Found {result['total_results']} papers")
            print(f"  - Execution time: {result.get('execution_time_ms', 'N/A')}ms")
            print(f"  - Parsed intent: {result['parsed_query']['intent']}")

            if result.get('generated_sparql'):
                print(f"\n  Generated SPARQL:")
                for line in result['generated_sparql'].split('\n')[:10]:
                    print(f"    {line}")

            if result['papers']:
                print(f"\n  First result: {result['papers'][0]['title'][:60]}...")
        else:
            print(f"✗ API error: {response.status_code}")
            print(f"  {response.text}")

    except ImportError:
        print("⚠ requests library not installed. Install with:")
        print("  pip install requests")
    except Exception as e:
        print(f"✗ FAIL: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("UNIFIED QUERY FLOW - TEST SUITE")
    print("=" * 70)

    test_query_parsing()
    test_sparql_generation()
    test_api_endpoint()

    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Start backend: cd backend && python run.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open browser: http://localhost:5173")
    print("4. Try example queries in the UI")
    print("\n")


if __name__ == "__main__":
    main()
