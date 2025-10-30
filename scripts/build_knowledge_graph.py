"""
Build RDF Knowledge Graph from Extracted Parameters.

Converts extracted parameters (from extract_parameters.py) into
RDF/Turtle format for loading into Apache Fuseki.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def normalize_value(value: float, unit: str, param_type: str) -> float:
    """
    Normalize parameter values to standard units.

    Temperature: normalized to keV
    Density: normalized to m^-3
    """
    if param_type == "temperature":
        # Convert to keV
        if unit.lower() == "kev":
            return value
        elif unit.lower() == "ev":
            return value / 1000.0
        elif unit.lower() == "k":
            # Kelvin to keV: 1 eV = 11604.5 K, so 1 K = 8.617e-5 eV
            return (value * 8.617e-5) / 1000.0
        else:
            return value

    elif param_type == "density":
        # Convert to m^-3
        if "m^-3" in unit or "m⁻³" in unit:
            return value
        elif "cm^-3" in unit or "cm⁻³" in unit:
            return value * 1e6  # cm^-3 to m^-3
        else:
            return value

    return value


def escape_ttl_string(s: str) -> str:
    """Escape special characters in TTL strings."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')


def build_knowledge_graph(input_file: str, output_file: str) -> None:
    """
    Build RDF knowledge graph from extracted parameters.

    Args:
        input_file: Path to extracted_with_llm.json
        output_file: Path to output TTL file
    """
    print("=" * 60)
    print("Building RDF Knowledge Graph")
    print("=" * 60)

    # Load extracted data
    print(f"\nLoading data from: {input_file}")
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Filter papers with parameters
    papers_with_params = [
        d for d in data
        if d['parameters']['temperature'] or d['parameters']['density']
    ]

    print(f"Total papers: {len(data)}")
    print(f"Papers with parameters: {len(papers_with_params)}")

    # Generate TTL content
    print("\nGenerating RDF triples...")

    ttl_lines = []

    # Prefixes
    ttl_lines.append("@prefix : <http://example.org/plasma#> .")
    ttl_lines.append("@prefix paper: <http://example.org/plasma/paper/> .")
    ttl_lines.append("@prefix meas: <http://example.org/plasma/measurement/> .")
    ttl_lines.append("@prefix param: <http://example.org/plasma/parameter/> .")
    ttl_lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
    ttl_lines.append("@prefix dcterms: <http://purl.org/dc/terms/> .")
    ttl_lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    ttl_lines.append("")

    # Header
    ttl_lines.append("# " + "=" * 44)
    ttl_lines.append(f"# Plasma Physics Knowledge Graph Data")
    ttl_lines.append(f"# Generated: {datetime.now().isoformat()}")
    ttl_lines.append(f"# Papers: {len(papers_with_params)}")
    ttl_lines.append("# " + "=" * 44)
    ttl_lines.append("")

    # Counters for measurements and parameters
    meas_counter = 1
    param_counter = 1

    # Process each paper
    for entry in papers_with_params:
        paper_id = entry['paper_id']
        title = escape_ttl_string(entry['title'])

        ttl_lines.append(f"# Paper: {title[:60]}...")
        ttl_lines.append(f"<http://example.org/plasma/paper/{paper_id}> a :Paper ;")
        ttl_lines.append(f'    :arxivId "{paper_id}" ;')
        ttl_lines.append(f'    :title "{title}" ;')

        # Collect all measurement URIs for this paper
        measurement_uris = []

        # Process temperatures
        for temp in entry['parameters']['temperature']:
            meas_uri = f"<http://example.org/plasma/measurement/m{meas_counter}>"
            measurement_uris.append(meas_uri)
            meas_counter += 1

        # Process densities
        for dens in entry['parameters']['density']:
            meas_uri = f"<http://example.org/plasma/measurement/m{meas_counter}>"
            measurement_uris.append(meas_uri)
            meas_counter += 1

        # Add reports relationships
        for meas_uri in measurement_uris:
            ttl_lines.append(f"    :reports {meas_uri} ;")

        # Remove last semicolon and add period
        ttl_lines[-1] = ttl_lines[-1][:-2] + " ."
        ttl_lines.append("")

    # Reset counter for measurements
    meas_counter = 1

    # Add measurement and parameter details
    for entry in papers_with_params:
        # Temperature measurements
        for temp in entry['parameters']['temperature']:
            param_uri = f"<http://example.org/plasma/parameter/p{param_counter}>"
            meas_uri = f"<http://example.org/plasma/measurement/m{meas_counter}>"

            # Measurement
            context = escape_ttl_string(temp.get('context', '')[:100])
            confidence = temp.get('confidence', 'medium')

            ttl_lines.append(f"{meas_uri} a :Measurement ;")
            ttl_lines.append(f"    :measuresParameter {param_uri} ;")
            ttl_lines.append(f'    :confidence "{confidence}" ;')
            ttl_lines.append(f'    :extractionMethod "regex+llm" ;')
            ttl_lines.append(f'    :context "{context}" ;')
            ttl_lines.append("    .")
            ttl_lines.append("")

            # Parameter
            value = temp.get('value', temp['value'])
            unit = temp.get('unit', temp['unit'])
            normalized = normalize_value(value, unit, 'temperature')

            ttl_lines.append(f"{param_uri} a :Temperature ;")
            ttl_lines.append(f"    :value {value} ;")
            ttl_lines.append(f'    :unitString "{unit}" ;')
            ttl_lines.append(f"    :normalizedValue {normalized} ;")
            ttl_lines.append("    .")
            ttl_lines.append("")

            meas_counter += 1
            param_counter += 1

        # Density measurements
        for dens in entry['parameters']['density']:
            param_uri = f"<http://example.org/plasma/parameter/p{param_counter}>"
            meas_uri = f"<http://example.org/plasma/measurement/m{meas_counter}>"

            # Measurement
            context = escape_ttl_string(dens.get('context', '')[:100])
            confidence = dens.get('confidence', 'medium')

            ttl_lines.append(f"{meas_uri} a :Measurement ;")
            ttl_lines.append(f"    :measuresParameter {param_uri} ;")
            ttl_lines.append(f'    :confidence "{confidence}" ;')
            ttl_lines.append(f'    :extractionMethod "regex+llm" ;')
            ttl_lines.append(f'    :context "{context}" ;')
            ttl_lines.append("    .")
            ttl_lines.append("")

            # Parameter
            value = dens.get('value', dens['value'])
            unit = dens.get('unit', dens['unit'])
            normalized = normalize_value(value, unit, 'density')

            ttl_lines.append(f"{param_uri} a :Density ;")
            ttl_lines.append(f"    :value {value} ;")
            ttl_lines.append(f'    :unitString "{unit}" ;')
            ttl_lines.append(f"    :normalizedValue {normalized} ;")
            ttl_lines.append("    .")
            ttl_lines.append("")

            meas_counter += 1
            param_counter += 1

    # Footer
    ttl_lines.append("# End of data")

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write('\n'.join(ttl_lines))

    print(f"\n✓ Knowledge graph saved to: {output_file}")
    print(f"  Papers: {len(papers_with_params)}")
    print(f"  Measurements: {meas_counter - 1}")
    print(f"  Parameters: {param_counter - 1}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Build RDF knowledge graph from extracted parameters"
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/extracted_with_llm.json',
        help='Input extracted parameters JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/plasma_data.ttl',
        help='Output TTL file'
    )

    args = parser.parse_args()

    build_knowledge_graph(args.input, args.output)

    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Load into Fuseki:")
    print(f"   - Visit http://localhost:3030")
    print(f"   - Upload {args.output} to your dataset")
    print("")
    print("2. Or use Docker:")
    print("   docker-compose restart fuseki")
    print("")
    print("3. Test the API:")
    print("   curl http://localhost:8000/health")
    print("=" * 60)


if __name__ == "__main__":
    main()
