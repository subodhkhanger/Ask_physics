#!/usr/bin/env python3
"""
Build bronze measurement labels with the repo's deterministic regex extractor.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def read_jsonl(path: Path) -> Iterable[Dict]:
    """Read JSONL records from disk."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def normalize_measurement(param_type: str, value: float, unit: str) -> tuple[Optional[float], Optional[str]]:
    """Normalize Ask Physics temperature and density units."""
    unit_lower = unit.lower()
    if param_type == "temperature":
        if unit_lower == "ev":
            return value * 0.001, "keV"
        if unit_lower == "k":
            return value * 8.617e-8, "keV"
        if unit_lower == "kev":
            return value, "keV"
        return None, None

    if param_type == "density":
        if "cm" in unit_lower or "centimeter" in unit_lower:
            return value * 1e6, "m^-3"
        if "m" in unit_lower or "meter" in unit_lower:
            return value, "m^-3"
        return None, None

    return None, None


def confidence_to_score(confidence: object) -> float:
    """Convert extractor confidence values into numeric scores."""
    if isinstance(confidence, (int, float)):
        return float(confidence)
    if confidence == "high":
        return 0.85
    if confidence == "medium":
        return 0.65
    if confidence == "low":
        return 0.35
    return 0.5


def build_measurements(extracted: Dict) -> List[Dict]:
    """Flatten the repo extractor output into the training label schema."""
    measurements: List[Dict] = []
    parameters = extracted.get("parameters", {})

    for param_type in ("temperature", "density"):
        for item in parameters.get(param_type, []) or []:
            if item.get("is_correct") is False:
                continue
            value = item.get("value")
            unit = item.get("unit")
            if value is None or unit is None:
                continue

            normalized_value, normalized_unit = normalize_measurement(param_type, float(value), str(unit))
            measurements.append(
                {
                    "type": param_type,
                    "value": float(value),
                    "unit": str(unit),
                    "normalized_value": normalized_value,
                    "normalized_unit": normalized_unit,
                    "context": item.get("context", ""),
                    "confidence": confidence_to_score(item.get("confidence")),
                }
            )

    return measurements


def paper_for_extractor(record: Dict) -> Dict:
    """Adapt raw metadata records to the existing ParameterExtractor input shape."""
    return {
        "id": record["paper_id"].replace("arxiv:", ""),
        "title": record["title"],
        "abstract": record["abstract"],
    }


def write_jsonl(records: Iterable[Dict], output_path: Path) -> int:
    """Write JSONL records and return the count."""
    count = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def build_label(record: Dict, extractor: object) -> Dict:
    """Build one bronze extraction label record."""
    extracted = extractor.extract_parameters(paper_for_extractor(record))
    return {
        "schema_version": "extraction_label.v1",
        "paper_id": record["paper_id"],
        "title": record["title"],
        "abstract": record["abstract"],
        "measurements": build_measurements(extracted),
        "source": {
            "source_url": record.get("source_url"),
            "pdf_url": record.get("pdf_url"),
            "categories": record.get("categories", []),
            "published": record.get("published"),
        },
        "label_provenance": {
            "method": "regex",
            "tool": "scripts.extract_parameters.ParameterExtractor",
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build bronze regex labels for Ask Physics QLoRA data.")
    parser.add_argument(
        "--input",
        default="training/data/raw/arxiv_metadata.jsonl",
        help="Raw paper metadata JSONL.",
    )
    parser.add_argument(
        "--output",
        default="training/data/bronze/regex_labels.jsonl",
        help="Output bronze label JSONL.",
    )
    args = parser.parse_args()

    try:
        from scripts.extract_parameters import ParameterExtractor
    except ImportError as exc:
        raise SystemExit(
            "Missing extraction dependencies. Install with "
            "`python3 -m pip install -r training/requirements.txt` or the repo requirements."
        ) from exc

    extractor = ParameterExtractor(use_llm=False)
    labels = (build_label(record, extractor) for record in read_jsonl(Path(args.input)))
    count = write_jsonl(labels, Path(args.output))

    print(f"Wrote {count} bronze labels to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
