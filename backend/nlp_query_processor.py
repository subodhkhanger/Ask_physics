"""
Natural Language Query Processor for Plasma Physics Queries.

Converts natural language queries like:
'Show me recent research on electron density in low-temperature plasmas between 10^16 and 10^18 m^-3'

Into structured parameters for SPARQL generation.
"""

import os
import re
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ParameterRange(BaseModel):
    """Represents a parameter range extracted from query."""
    type: str  # "temperature" or "density"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str
    normalized_min: Optional[float] = None
    normalized_max: Optional[float] = None


class ParsedQuery(BaseModel):
    """Structured representation of parsed natural language query."""
    intent: str  # "search", "statistics", "compare"
    parameters: Dict[str, ParameterRange] = {}
    keywords: List[str] = []
    temporal_constraint: Optional[str] = None  # "recent", "2023", etc.
    confidence: float = 0.0
    original_query: str
    raw_llm_response: Optional[str] = None


class NLPQueryProcessor:
    """
    Processes natural language physics queries using LLM.

    Two-stage approach:
    1. LLM extracts structured parameters
    2. Post-process and normalize values
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.use_llm = OPENAI_AVAILABLE

        if self.use_llm:
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: No OpenAI API key found. Falling back to regex.")
                self.use_llm = False
            else:
                self.client = OpenAI(api_key=api_key)

    def parse(self, query: str) -> ParsedQuery:
        """
        Main entry point: Parse natural language query.

        Args:
            query: Natural language query string

        Returns:
            ParsedQuery with structured parameters
        """
        if self.use_llm:
            return self._parse_with_llm(query)
        else:
            return self._parse_with_regex(query)

    def _parse_with_llm(self, query: str) -> ParsedQuery:
        """Use LLM to extract structured parameters."""

        prompt = f"""You are a plasma physics query parser. Extract structured information from this query:

Query: "{query}"

Extract the following in JSON format:
1. intent: "search" (find papers), "statistics" (get stats), or "compare" (compare values)
2. parameters: dict with "temperature" and/or "density" containing:
   - min_value: minimum value (number or null)
   - max_value: maximum value (number or null)
   - unit: unit of measurement (keV, eV, K for temp; m^-3, cm^-3 for density)
3. keywords: list of physics domain keywords (e.g., ["tokamak", "plasma", "confinement"])
4. temporal_constraint: "recent" (last 2 years), "YYYY" (specific year), or null

Handle scientific notation like:
- "10^16 to 10^18 m^-3" → min: 1e16, max: 1e18
- "between 5 and 10 keV" → min: 5, max: 10
- "above 10 keV" → min: 10, max: null
- "low temperature" → max: 1 keV (infer)

Return ONLY valid JSON, no markdown:
{{
  "intent": "search",
  "parameters": {{
    "temperature": {{"min_value": 5.0, "max_value": 10.0, "unit": "keV"}},
    "density": {{"min_value": 1e16, "max_value": 1e18, "unit": "m^-3"}}
  }},
  "keywords": ["plasma", "electron"],
  "temporal_constraint": "recent",
  "confidence": 0.9
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[{"role": "user", "content": prompt}],
                temperature=0  # Deterministic
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = re.sub(r'^```(?:json)?\n', '', content)
                content = re.sub(r'\n```$', '', content)

            parsed_data = json.loads(content)

            # Convert to ParameterRange objects
            parameters = {}
            for param_type, param_data in parsed_data.get('parameters', {}).items():
                if param_data:
                    param_range = ParameterRange(
                        type=param_type,
                        min_value=param_data.get('min_value'),
                        max_value=param_data.get('max_value'),
                        unit=param_data.get('unit', 'unknown')
                    )
                    # Normalize values
                    self._normalize_parameter(param_range)
                    parameters[param_type] = param_range

            return ParsedQuery(
                intent=parsed_data.get('intent', 'search'),
                parameters=parameters,
                keywords=parsed_data.get('keywords', []),
                temporal_constraint=parsed_data.get('temporal_constraint'),
                confidence=parsed_data.get('confidence', 0.8),
                original_query=query,
                raw_llm_response=content
            )

        except Exception as e:
            print(f"LLM parsing failed: {e}")
            print(f"Response: {content if 'content' in locals() else 'N/A'}")
            # Fallback to regex
            return self._parse_with_regex(query)

    def _parse_with_regex(self, query: str) -> ParsedQuery:
        """Fallback: Simple regex-based extraction."""
        parameters = {}
        keywords = []

        # Extract temperature
        temp_match = re.search(
            r'temperature.*?(\d+\.?\d*)\s*(?:to|-)?\s*(\d+\.?\d*)?\s*(keV|eV|K)',
            query, re.IGNORECASE
        )
        if temp_match:
            min_val = float(temp_match.group(1))
            max_val = float(temp_match.group(2)) if temp_match.group(2) else None
            unit = temp_match.group(3)
            param = ParameterRange(
                type="temperature",
                min_value=min_val,
                max_value=max_val,
                unit=unit
            )
            self._normalize_parameter(param)
            parameters['temperature'] = param

        # Extract density
        density_match = re.search(
            r'density.*?(\d+\.?\d*)\s*[×x]?\s*10[\^]?([+-]?\d+).*?(?:to|and)?\s*(\d+\.?\d*)\s*[×x]?\s*10[\^]?([+-]?\d+)?\s*(m\^?-?3|cm\^?-?3)',
            query, re.IGNORECASE
        )
        if density_match:
            min_val = float(density_match.group(1)) * (10 ** int(density_match.group(2)))
            max_val_base = density_match.group(3)
            max_val_exp = density_match.group(4)
            if max_val_base and max_val_exp:
                max_val = float(max_val_base) * (10 ** int(max_val_exp))
            else:
                max_val = None
            unit = density_match.group(5)

            param = ParameterRange(
                type="density",
                min_value=min_val,
                max_value=max_val,
                unit=unit
            )
            self._normalize_parameter(param)
            parameters['density'] = param

        # Extract keywords
        physics_keywords = ['tokamak', 'plasma', 'fusion', 'confinement', 'electron', 'ion']
        for keyword in physics_keywords:
            if keyword in query.lower():
                keywords.append(keyword)

        # Temporal
        temporal = None
        if 'recent' in query.lower():
            temporal = 'recent'

        return ParsedQuery(
            intent='search',
            parameters=parameters,
            keywords=keywords,
            temporal_constraint=temporal,
            confidence=0.5,  # Lower confidence for regex
            original_query=query
        )

    def _normalize_parameter(self, param: ParameterRange) -> None:
        """Normalize parameter values to standard units."""
        if param.type == "temperature":
            # Normalize to keV
            if param.unit.lower() == 'ev':
                factor = 0.001
            elif param.unit.lower() == 'k':
                factor = 8.617e-8  # Kelvin to keV
            else:  # keV
                factor = 1.0

            param.normalized_min = param.min_value * factor if param.min_value else None
            param.normalized_max = param.max_value * factor if param.max_value else None

        elif param.type == "density":
            # Normalize to m^-3
            if 'cm' in param.unit.lower():
                factor = 1e6  # cm^-3 to m^-3
            else:
                factor = 1.0

            param.normalized_min = param.min_value * factor if param.min_value else None
            param.normalized_max = param.max_value * factor if param.max_value else None


# Example usage
if __name__ == "__main__":
    processor = NLPQueryProcessor()

    test_queries = [
        "Show me recent research on electron density in low-temperature plasmas between 10^16 and 10^18 m^-3",
        "Find papers with temperature above 10 keV",
        "Recent tokamak experiments",
        "Density between 1e19 and 1e20 m^-3 in fusion plasmas"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = processor.parse(query)
        print(f"Parsed: {parsed.model_dump_json(indent=2)}")
