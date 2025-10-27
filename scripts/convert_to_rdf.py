#!/usr/bin/env python3
"""
Convert extracted parameters from JSON to RDF triples (Turtle format).

This script transforms the parameter extraction results into an RDF knowledge graph
following the plasma physics ontology.

Usage:
    python scripts/convert_to_rdf.py --input data/sample_extracted_params.json --output data/plasma_data.ttl
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import quote


class RDFConverter:
    """Convert extracted plasma parameters to RDF triples."""

    def __init__(self):
        self.namespace = "http://example.org/plasma#"
        self.paper_ns = "http://example.org/plasma/paper/"
        self.measurement_ns = "http://example.org/plasma/measurement/"
        self.param_ns = "http://example.org/plasma/parameter/"

    def escape_string(self, s: str) -> str:
        """Escape special characters for Turtle format."""
        if not s:
            return ""
        # Escape backslashes first, then quotes, then newlines
        s = s.replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace('\n', '\\n')
        s = s.replace('\r', '\\r')
        return s

    def create_uri(self, base: str, identifier: str) -> str:
        """Create a valid URI from base and identifier."""
        # Remove problematic characters and use quote for URL encoding
        safe_id = quote(identifier.replace(' ', '_').replace('/', '_'), safe='')
        return f"{base}{safe_id}"

    def normalize_temperature(self, value: float, unit: str) -> float:
        """Normalize temperature to keV."""
        if unit.lower() == 'kev':
            return value
        elif unit.lower() == 'ev':
            return value / 1000.0
        elif unit.lower() == 'k':
            # Kelvin to keV: multiply by Boltzmann constant (8.617333e-5 eV/K)
            return value * 8.617333e-5 / 1000.0
        return value

    def normalize_density(self, value: float, unit: str) -> float:
        """Normalize density to m^-3."""
        if 'm^-3' in unit.lower() or 'm-3' in unit.lower():
            return value
        elif 'cm^-3' in unit.lower() or 'cm-3' in unit.lower():
            return value * 1e6  # cm^-3 to m^-3
        return value

    def convert_to_ttl(self, papers: List[Dict[str, Any]]) -> str:
        """Convert papers with extracted parameters to Turtle format."""

        lines = []

        # Header with prefixes
        lines.append("@prefix : <http://example.org/plasma#> .")
        lines.append("@prefix paper: <http://example.org/plasma/paper/> .")
        lines.append("@prefix meas: <http://example.org/plasma/measurement/> .")
        lines.append("@prefix param: <http://example.org/plasma/parameter/> .")
        lines.append("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .")
        lines.append("@prefix dcterms: <http://purl.org/dc/terms/> .")
        lines.append("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
        lines.append("")
        lines.append("# ============================================")
        lines.append("# Plasma Physics Knowledge Graph Data")
        lines.append(f"# Generated: {datetime.now().isoformat()}")
        lines.append(f"# Papers: {len(papers)}")
        lines.append("# ============================================")
        lines.append("")

        measurement_counter = 0
        param_counter = 0

        for paper_data in papers:
            paper_id = paper_data.get('id', 'unknown')
            paper_uri = self.create_uri(self.paper_ns, paper_id)

            # Paper entity
            lines.append(f"# Paper: {self.escape_string(paper_data.get('title', 'Untitled'))[:80]}")
            lines.append(f"<{paper_uri}> a :Paper ;")
            lines.append(f'    :arxivId "{self.escape_string(paper_id)}" ;')

            if 'title' in paper_data:
                lines.append(f'    :title "{self.escape_string(paper_data["title"])}" ;')

            if 'authors' in paper_data:
                # Join authors if it's a list
                authors = paper_data['authors']
                if isinstance(authors, list):
                    authors = ', '.join(authors)
                lines.append(f'    :authors "{self.escape_string(str(authors))}" ;')

            if 'published' in paper_data:
                lines.append(f'    :publicationDate "{paper_data["published"]}"^^xsd:dateTime ;')

            if 'pdf_url' in paper_data:
                lines.append(f'    :pdfUrl <{paper_data["pdf_url"]}> ;')

            if 'summary' in paper_data:
                abstract = paper_data['summary'][:500]  # Limit length
                lines.append(f'    :abstract "{self.escape_string(abstract)}" ;')

            # Process parameters
            params = paper_data.get('parameters', {})

            # Temperature measurements
            temperatures = params.get('temperature', [])
            for i, temp in enumerate(temperatures):
                measurement_counter += 1
                param_counter += 1

                meas_uri = f"{self.measurement_ns}m{measurement_counter}"
                param_uri = f"{self.param_ns}p{param_counter}"

                lines.append(f'    :reports <{meas_uri}> ;')

            # Density measurements
            densities = params.get('density', [])
            for i, dens in enumerate(densities):
                measurement_counter += 1
                param_counter += 1

                meas_uri = f"{self.measurement_ns}m{measurement_counter}"
                param_uri = f"{self.param_ns}p{param_counter}"

                lines.append(f'    :reports <{meas_uri}> ;')

            # Remove trailing semicolon and add period
            if lines[-1].endswith(';'):
                lines[-1] = lines[-1][:-1] + '.'
            else:
                lines[-1] += ' .'

            lines.append("")

            # Now define all measurements and parameters
            # Temperature measurements
            param_counter_temp = param_counter - len(temperatures) - len(densities) + 1
            measurement_counter_temp = measurement_counter - len(temperatures) - len(densities) + 1

            for i, temp in enumerate(temperatures):
                meas_uri = f"{self.measurement_ns}m{measurement_counter_temp}"
                param_uri = f"{self.param_ns}p{param_counter_temp}"

                value = temp.get('value', 0)
                unit = temp.get('unit', 'keV')
                confidence = temp.get('confidence', 'medium')
                context = temp.get('context', '')

                # Normalize value
                normalized = self.normalize_temperature(value, unit)

                lines.append(f"<{meas_uri}> a :Measurement ;")
                lines.append(f"    :measuresParameter <{param_uri}> ;")
                lines.append(f'    :confidence "{confidence}" ;')
                lines.append(f'    :extractionMethod "regex" ;')

                if context:
                    lines.append(f'    :context "{self.escape_string(context[:200])}" ;')

                lines.append("    .")
                lines.append("")

                lines.append(f"<{param_uri}> a :Temperature ;")
                lines.append(f"    :value {value} ;")
                lines.append(f'    :unitString "{unit}" ;')
                lines.append(f"    :normalizedValue {normalized} ;")
                lines.append("    .")
                lines.append("")

                measurement_counter_temp += 1
                param_counter_temp += 1

            # Density measurements
            for i, dens in enumerate(densities):
                meas_uri = f"{self.measurement_ns}m{measurement_counter_temp}"
                param_uri = f"{self.param_ns}p{param_counter_temp}"

                value = dens.get('value', 0)
                unit = dens.get('unit', 'm^-3')
                confidence = dens.get('confidence', 'medium')
                context = dens.get('context', '')

                # Normalize value
                normalized = self.normalize_density(value, unit)

                lines.append(f"<{meas_uri}> a :Measurement ;")
                lines.append(f"    :measuresParameter <{param_uri}> ;")
                lines.append(f'    :confidence "{confidence}" ;')
                lines.append(f'    :extractionMethod "regex" ;')

                if context:
                    lines.append(f'    :context "{self.escape_string(context[:200])}" ;')

                lines.append("    .")
                lines.append("")

                lines.append(f"<{param_uri}> a :Density ;")
                lines.append(f"    :value {value} ;")
                lines.append(f'    :unitString "{unit}" ;')
                lines.append(f"    :normalizedValue {normalized} ;")
                lines.append("    .")
                lines.append("")

                measurement_counter_temp += 1
                param_counter_temp += 1

        lines.append("# End of data")

        return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert extracted parameters to RDF (Turtle format)'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input JSON file with extracted parameters'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output Turtle file (.ttl)'
    )

    args = parser.parse_args()

    # Load input data
    print(f"Loading data from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    print(f"Found {len(papers)} papers")

    # Convert to RDF
    print("Converting to RDF triples...")
    converter = RDFConverter()
    ttl_content = converter.convert_to_ttl(papers)

    # Count triples (approximate by counting periods)
    triple_count = ttl_content.count(' .') + ttl_content.count(' ;\n')

    # Save output
    print(f"Writing {triple_count} triples to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(ttl_content)

    print(f"✓ Successfully created {args.output}")
    print(f"  Papers: {len(papers)}")
    print(f"  Triples: ~{triple_count}")

    # Summary statistics
    temp_count = sum(len(p.get('parameters', {}).get('temperature', [])) for p in papers)
    dens_count = sum(len(p.get('parameters', {}).get('density', [])) for p in papers)

    print(f"  Temperature measurements: {temp_count}")
    print(f"  Density measurements: {dens_count}")


if __name__ == '__main__':
    main()
