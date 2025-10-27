"""
Extract physical parameters from plasma physics papers.

Following SKILLS.md two-pass approach:
1. Regex for structure (fast, gets ~70%)
2. LLM validation (slow but accurate, gets to ~90%)
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if OpenAI is available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Run: pip install openai")


class ParameterExtractor:
    """
    Extract physical parameters from scientific text.

    Design principles (from SKILLS.md):
    1. Regex for structure, LLM for context
    2. Always include context snippet (proves extraction is correct)
    3. Normalize units immediately
    4. Return confidence scores
    """

    # Temperature patterns - ordered by specificity (most specific first)
    TEMP_PATTERNS = [
        # Pattern with explicit parameter name
        r'(?:electron temperature|T_?e|ion temperature|T_?i)[\s:=~]*'
        r'(?:of|about|approximately|around)?[\s]*'
        r'(\d+\.?\d*)[\s]*([×x]\s*10\^?[+-]?\d+)?[\s]*(keV|eV|K)',

        # Pattern with context words
        r'(?:peak|maximum|central|average|typical)\s+temperatures?[\s:=~]*'
        r'(?:of|about|approximately|around)?[\s]*'
        r'(\d+\.?\d*)[\s]*([×x]\s*10\^?[+-]?\d+)?[\s]*(keV|eV|K)',

        # Generic temperature with units (least specific, most false positives)
        r'(\d+\.?\d*)[\s]*([×x]\s*10\^?[+-]?\d+)?[\s]*(keV|eV|K)',
    ]

    DENSITY_PATTERNS = [
        # Explicit density with scientific notation and units
        r'(?:electron density|n_?e|ion density|n_?i|plasma density)[\s:=~]*'
        r'(?:of|about|approximately|around)?[\s]*'
        r'(\d+\.?\d*)[\s]*[×x]\s*10[¹²³⁴⁵⁶⁷⁸⁹⁰\^]?([+-]?\d+)[\s]*(m\^?-?3|cm\^?-?3|per cubic meter|per cubic centimeter)',

        # Density with scientific notation (more permissive)
        r'density[\s:=~]*'
        r'(?:of|about|approximately|around)?[\s]*'
        r'(\d+\.?\d*)[\s]*[×x]\s*10[¹²³⁴⁵⁶⁷⁸⁹⁰\^]?([+-]?\d+)[\s]*(m\^?-?3|cm\^?-?3)',
    ]

    def __init__(self, use_llm: bool = True, api_key: Optional[str] = None):
        """
        Initialize extractor.

        Args:
            use_llm: Whether to use LLM validation (recommended)
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.use_llm = use_llm and OPENAI_AVAILABLE

        if self.use_llm:
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
                print("  Falling back to regex-only extraction (lower accuracy)")
                self.use_llm = False
            else:
                self.client = OpenAI(api_key=api_key)
                print("✓ Using LLM validation for higher accuracy")
        else:
            print("! Using regex-only extraction (consider adding OpenAI API key)")

    def extract_with_regex(self, text: str, param_type: str) -> List[Dict]:
        """First pass: regex extraction."""
        patterns = self.TEMP_PATTERNS if param_type == 'temperature' else self.DENSITY_PATTERNS
        matches = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Extract context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()

                # Parse value
                try:
                    groups = match.groups()
                    value = float(groups[0])

                    # Handle scientific notation if present (group 2)
                    if len(groups) > 1 and groups[1]:
                        exponent_str = groups[1].replace('×', '').replace('x', '').replace('10^', '').replace('10', '').strip()
                        if exponent_str:
                            try:
                                exponent = float(exponent_str)
                                value = value * (10 ** exponent)
                            except ValueError:
                                pass  # Keep original value if exponent parsing fails

                    # Unit is the last captured group
                    unit = groups[-1]

                    matches.append({
                        'value': value,
                        'unit': unit,
                        'context': context,
                        'confidence': 'high' if 'electron' in match.group(0).lower() else 'medium'
                    })
                except (ValueError, IndexError, AttributeError) as e:
                    continue  # Skip malformed matches

        # Remove duplicates based on value and context similarity
        unique_matches = []
        for match in matches:
            is_duplicate = False
            for existing in unique_matches:
                if (abs(match['value'] - existing['value']) < 0.01 and
                    match['unit'] == existing['unit']):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_matches.append(match)

        return unique_matches

    def validate_with_llm(self, text: str, regex_results: List[Dict], param_type: str) -> List[Dict]:
        """
        Second pass: LLM validates and finds missed parameters.

        This is the secret sauce - regex gets you 70%, LLM gets you to 90%+.
        """
        if not self.use_llm:
            return regex_results

        prompt = f"""Extract {param_type} values from this scientific abstract.

Abstract: {text}

Instructions:
1. Find all {param_type} measurements with their units
2. Include the context sentence for each value
3. Mark confidence as 'high' if explicitly stated, 'medium' if inferred, 'low' if uncertain

Regex found these (validate if correct):
{json.dumps(regex_results, indent=2)}

Return ONLY valid JSON in this exact format (no markdown, no explanation):
[
  {{
    "type": "{param_type}",
    "value": <number>,
    "unit": "<unit>",
    "context": "<sentence with the measurement>",
    "confidence": "high|medium|low",
    "is_correct": true
  }}
]

If no {param_type} values found, return: []
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Good balance of cost/accuracy
                messages=[{"role": "user", "content": prompt}],
                temperature=0  # Deterministic extraction
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            validated = json.loads(content)
            return validated if validated else regex_results

        except json.JSONDecodeError as e:
            print(f"  ! Warning: LLM returned invalid JSON: {e}")
            print(f"    Falling back to regex results")
            return regex_results
        except Exception as e:
            print(f"  ! Warning: LLM validation failed: {e}")
            return regex_results

    def extract_parameters(self, paper: Dict) -> Dict:
        """
        Main extraction pipeline.

        Returns all extracted parameters with metadata.
        """
        text = paper['abstract']

        # Extract temperatures
        temp_regex = self.extract_with_regex(text, 'temperature')
        temperatures = self.validate_with_llm(text, temp_regex, 'temperature') if temp_regex else []

        # Extract densities
        density_regex = self.extract_with_regex(text, 'density')
        densities = self.validate_with_llm(text, density_regex, 'density') if density_regex else []

        return {
            'paper_id': paper['id'],
            'title': paper['title'],
            'parameters': {
                'temperature': temperatures,
                'density': densities
            },
            'extraction_date': datetime.now().isoformat(),
            'extraction_method': 'regex+llm' if self.use_llm else 'regex_only'
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract parameters from collected papers"
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/papers.json',
        help='Input papers JSON file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/extracted_params.json',
        help='Output extracted parameters JSON file'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM validation (faster but less accurate)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Enable manual validation mode (pauses after each paper)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Phase 1: Parameter Extraction")
    print("=" * 60)

    # Load papers
    try:
        with open(args.input, 'r') as f:
            papers = json.load(f)
        print(f"✓ Loaded {len(papers)} papers from {args.input}")
    except FileNotFoundError:
        print(f"✗ Error: {args.input} not found")
        print("  Run: python scripts/collect_papers.py first")
        return 1

    # Initialize extractor
    extractor = ParameterExtractor(use_llm=not args.no_llm)

    # Extract parameters
    results = []
    stats = {'temp_found': 0, 'density_found': 0, 'neither': 0}

    print(f"\nExtracting parameters from {len(papers)} papers...")
    for i, paper in enumerate(papers):
        print(f"\n[{i+1}/{len(papers)}] {paper['id']}: {paper['title'][:60]}...")

        result = extractor.extract_parameters(paper)
        results.append(result)

        # Statistics
        temp_count = len(result['parameters']['temperature'])
        dens_count = len(result['parameters']['density'])

        if temp_count > 0:
            stats['temp_found'] += 1
            print(f"  ✓ Found {temp_count} temperature value(s)")
        if dens_count > 0:
            stats['density_found'] += 1
            print(f"  ✓ Found {dens_count} density value(s)")
        if temp_count == 0 and dens_count == 0:
            stats['neither'] += 1
            print(f"  - No parameters found")

        # Manual validation mode
        if args.validate:
            print("\n  --- MANUAL VALIDATION ---")
            print(f"  Temperatures: {result['parameters']['temperature']}")
            print(f"  Densities: {result['parameters']['density']}")
            input("  Press Enter if correct, Ctrl+C to stop...")

    # Save results
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("=== EXTRACTION SUMMARY ===")
    print("=" * 60)
    print(f"Papers processed: {len(papers)}")
    print(f"Papers with temperature: {stats['temp_found']} ({stats['temp_found']/len(papers)*100:.1f}%)")
    print(f"Papers with density: {stats['density_found']} ({stats['density_found']/len(papers)*100:.1f}%)")
    print(f"Papers with neither: {stats['neither']} ({stats['neither']/len(papers)*100:.1f}%)")
    print(f"\n✓ Results saved to: {args.output}")

    # Recommendation
    print("\n" + "=" * 60)
    print("NEXT STEPS (from SKILLS.md):")
    print("=" * 60)
    if len(papers) < 20:
        print("1. ⚠️  CRITICAL: Manually validate these extractions")
        print("   Open data/extracted_params.json and check accuracy")
        print("   Goal: >70% accuracy required before scaling up")
        print("\n2. If accuracy acceptable:")
        print("   python scripts/collect_papers.py --limit 100")
        print("   python scripts/extract_parameters.py")
    else:
        print("✓ You have a good-sized dataset!")
        print("  Next: Build the knowledge graph (Phase 2)")

    return 0


if __name__ == "__main__":
    exit(main())
