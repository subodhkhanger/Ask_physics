#!/usr/bin/env python3
"""
Prepare model-neutral SFT data for Ask Physics natural-language query parsing.

The examples teach an open model to replace the OpenAI-backed parser in
backend/nlp_query_processor.py. The model should emit strict JSON that the
backend can normalize and pass to DynamicSPARQLBuilder.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional


SYSTEM_PROMPT = (
    "Parse plasma physics literature search queries into strict JSON. "
    "Return only valid JSON with intent, parameters, keywords, "
    "temporal_constraint, and confidence. Use intent search for paper search "
    "and statistics for aggregate requests. Parameters may contain temperature "
    "and density objects with min_value, max_value, and unit. Use null when a "
    "bound is absent. Do not include normalized values."
)


KEYWORDS = [
    "tokamak",
    "stellarator",
    "fusion plasma",
    "low-temperature plasma",
    "helicon plasma",
    "plasma wakefield accelerator",
    "magnetic reconnection",
    "warm dense matter",
    "laser plasma",
    "ionosphere",
    "divertor",
    "electron beam",
    "edge plasma",
    "scrape-off layer",
    "plasma sheath",
    "radio-frequency plasma",
    "capacitively coupled plasma",
    "inductively coupled plasma",
    "plasma diagnostics",
    "solar wind",
    "magnetosphere",
    "pulsar wind nebula",
    "pair plasma",
    "dusty plasma",
    "microdischarge",
    "plasma catalysis",
    "plasma turbulence",
    "gyrokinetic simulation",
    "ion beam",
    "neutral beam",
    "warm plasma",
    "cold plasma",
]

TEMPERATURE_RANGES = [
    (1.0, 10.0, "keV"),
    (500.0, 1500.0, "eV"),
    (100000.0, 1000000.0, "K"),
    (0.2, 2.0, "keV"),
    (5.0, 20.0, "keV"),
    (50.0, 250.0, "eV"),
    (2.5, 7.5, "keV"),
    (300.0, 800.0, "K"),
    (10000.0, 50000.0, "K"),
    (0.05, 0.5, "keV"),
]

TEMPERATURE_THRESHOLDS = [
    ("above", 10.0, None, "keV"),
    ("below", None, 1.0, "keV"),
    ("greater than", 750.0, None, "eV"),
    ("less than", None, 500000.0, "K"),
    ("at least", 2.0, None, "keV"),
    ("under", None, 200.0, "eV"),
    ("over", 100000.0, None, "K"),
]

DENSITY_RANGES = [
    (1e16, 1e18, "m^-3"),
    (1e19, 1e20, "m^-3"),
    (1e12, 1e14, "cm^-3"),
    (5e17, 5e19, "m^-3"),
    (1e10, 5e11, "cm^-3"),
    (1e15, 1e17, "m^-3"),
    (2e18, 8e19, "m^-3"),
    (5e11, 5e13, "cm^-3"),
    (1e20, 5e21, "m^-3"),
    (1e8, 1e10, "cm^-3"),
]

DENSITY_THRESHOLDS = [
    ("above", 1e19, None, "m^-3"),
    ("below", None, 1e18, "m^-3"),
    ("greater than", 1e13, None, "cm^-3"),
    ("less than", None, 5e11, "cm^-3"),
    ("at least", 5e18, None, "m^-3"),
    ("under", None, 1e12, "cm^-3"),
    ("over", 1e20, None, "m^-3"),
]

TEMPORAL_VARIANTS = [
    ("recent ", "recent"),
    ("2024 ", "2024"),
    ("2025 ", "2025"),
    ("2023 ", "2023"),
    ("", None),
]

TEMPERATURE_ALIASES = [
    "temperature",
    "electron temperature",
    "ion temperature",
    "Te",
    "T_e",
]

DENSITY_ALIASES = [
    "density",
    "electron density",
    "plasma density",
    "number density",
    "ne",
    "n_e",
]

SEARCH_PREFIXES = [
    "find",
    "show me",
    "search for",
    "list",
    "retrieve",
]

RANGE_CONNECTORS = [
    "between {min} and {max} {unit}",
    "from {min} to {max} {unit}",
    "{min}-{max} {unit}",
    "{min} to {max} {unit}",
]

KEYWORD_ONLY_TEMPLATES = [
    "{prefix}papers about {keyword}",
    "{prefix}{keyword} papers",
    "{prefix}research on {keyword}",
    "{prefix}literature for {keyword}",
    "{prefix}articles related to {keyword}",
]

NEGATIVE_QUERIES = [
    "papers about plasma diagnostics near 110 km altitude",
    "tokamak papers with magnetic field around 5 T",
    "laser plasma studies using 800 nm wavelength",
    "find papers with pulse duration below 30 fs",
    "recent ionosphere papers at 300 km altitude",
    "papers about divertor heat flux above 10 MW/m2",
    "stellarator papers with confinement time around 100 ms",
    "plasma catalysis papers with 40 percent conversion",
    "electron beam papers with energy around 1 MeV",
    "find simulations using grid size 512 by 512",
    "papers with RF frequency around 13.56 MHz",
    "show studies using 20 kW power",
    "recent papers with magnetic field over 2 Tesla",
    "plasma papers with pressure below 1 Pa",
    "warm dense matter papers with density functional theory",
]


def split_for_id(example_id: str, dev_percent: int, test_percent: int) -> str:
    """Assign a deterministic split from the example ID hash."""
    bucket = int(hashlib.sha256(example_id.encode("utf-8")).hexdigest(), 16) % 100
    if bucket < test_percent:
        return "test"
    if bucket < test_percent + dev_percent:
        return "dev"
    return "train"


def parameter(
    param_type: str,
    min_value: Optional[float],
    max_value: Optional[float],
    unit: str,
) -> Dict:
    """Build a parser output parameter object."""
    return {
        "type": param_type,
        "min_value": min_value,
        "max_value": max_value,
        "unit": unit,
    }


def output_payload(
    intent: str,
    parameters: Dict[str, Dict],
    keywords: List[str],
    temporal_constraint: Optional[str] = None,
    confidence: float = 0.95,
) -> str:
    """Serialize the strict JSON assistant payload."""
    payload = {
        "intent": intent,
        "parameters": parameters,
        "keywords": keywords,
        "temporal_constraint": temporal_constraint,
        "confidence": confidence,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def fmt(value: float) -> str:
    """Format numbers for compact user-query text."""
    return f"{value:g}"


def record(example_id: str, query: str, assistant_content: str) -> Dict:
    """Build one model-neutral SFT chat record."""
    return {
        "schema_version": "sft_chat.v1",
        "example_id": example_id,
        "task": "query_parsing",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
            {"role": "assistant", "content": assistant_content},
        ],
    }


def stratum_key(item: Dict) -> str:
    """Return a coarse bucket key for balanced downsampling."""
    payload = json.loads(item["messages"][-1]["content"])
    parameters = payload.get("parameters", {})
    param_key = "+".join(sorted(parameters.keys())) if parameters else "none"
    temporal = payload.get("temporal_constraint") or "none"
    return f"{payload.get('intent')}|{param_key}|{temporal}"


def select_balanced(records: List[Dict], max_examples: Optional[int]) -> List[Dict]:
    """Select a deterministic, roughly balanced subset across parser buckets."""
    if max_examples is None or len(records) <= max_examples:
        return records

    buckets: Dict[str, List[Dict]] = {}
    for item in records:
        buckets.setdefault(stratum_key(item), []).append(item)

    selected = []
    while len(selected) < max_examples:
        made_progress = False
        for key in sorted(buckets):
            bucket = buckets[key]
            if bucket:
                selected.append(bucket.pop(0))
                made_progress = True
                if len(selected) >= max_examples:
                    break
        if not made_progress:
            break

    return sorted(selected, key=lambda item: item["example_id"])


def make_examples() -> Iterable[Dict]:
    """Generate deterministic query parsing examples."""
    index = 1

    for keyword in KEYWORDS:
        for prefix, temporal in TEMPORAL_VARIANTS:
            for template in KEYWORD_ONLY_TEMPLATES:
                query = template.format(prefix=prefix, keyword=keyword).strip()
                yield record(
                    f"query-parse-{index:05d}",
                    query,
                    output_payload("search", {}, [keyword], temporal, 0.92),
                )
                index += 1

    for query in NEGATIVE_QUERIES:
        yield record(
            f"query-parse-{index:05d}",
            query,
            output_payload("search", {}, [], None, 0.86),
        )
        index += 1

    for keyword in KEYWORDS:
        for min_value, max_value, unit in TEMPERATURE_RANGES:
            for alias in TEMPERATURE_ALIASES:
                for connector in RANGE_CONNECTORS:
                    range_text = connector.format(min=fmt(min_value), max=fmt(max_value), unit=unit)
                    payload = output_payload(
                        "search",
                        {"temperature": parameter("temperature", min_value, max_value, unit)},
                        [keyword],
                    )
                    queries = [
                        f"find {keyword} papers with {alias} {range_text}",
                        f"{keyword} research where {alias} is {range_text}",
                    ]
                    for query in queries:
                        yield record(f"query-parse-{index:05d}", query, payload)
                        index += 1

    for keyword in KEYWORDS:
        for operator, min_value, max_value, unit in TEMPERATURE_THRESHOLDS:
            for alias in TEMPERATURE_ALIASES:
                for search_prefix in SEARCH_PREFIXES[:3]:
                    query = f"{search_prefix} {keyword} papers with {alias} {operator} {fmt(min_value or max_value)} {unit}"
                    yield record(
                        f"query-parse-{index:05d}",
                        query,
                        output_payload(
                            "search",
                            {"temperature": parameter("temperature", min_value, max_value, unit)},
                            [keyword],
                        ),
                    )
                    index += 1

    for keyword in KEYWORDS:
        for min_value, max_value, unit in DENSITY_RANGES:
            for alias in DENSITY_ALIASES:
                for connector in RANGE_CONNECTORS:
                    range_text = connector.format(min=fmt(min_value), max=fmt(max_value), unit=unit)
                    payload = output_payload(
                        "search",
                        {"density": parameter("density", min_value, max_value, unit)},
                        [keyword],
                    )
                    queries = [
                        f"find {keyword} papers with {alias} {range_text}",
                        f"{keyword} experiments where {alias} is {range_text}",
                    ]
                    for query in queries:
                        yield record(f"query-parse-{index:05d}", query, payload)
                        index += 1

    for keyword in KEYWORDS:
        for operator, min_value, max_value, unit in DENSITY_THRESHOLDS:
            for alias in DENSITY_ALIASES:
                for search_prefix in SEARCH_PREFIXES[:3]:
                    query = f"{search_prefix} {keyword} papers with {alias} {operator} {fmt(min_value or max_value)} {unit}"
                    yield record(
                        f"query-parse-{index:05d}",
                        query,
                        output_payload(
                            "search",
                            {"density": parameter("density", min_value, max_value, unit)},
                            [keyword],
                        ),
                    )
                    index += 1

    for keyword in KEYWORDS:
        for temp_range, density_range in zip(TEMPERATURE_RANGES, DENSITY_RANGES):
            t_min, t_max, t_unit = temp_range
            d_min, d_max, d_unit = density_range
            query = (
                f"recent {keyword} papers with temperature between {fmt(t_min)} and {fmt(t_max)} {t_unit} "
                f"and density between {fmt(d_min)} and {fmt(d_max)} {d_unit}"
            )
            yield record(
                f"query-parse-{index:05d}",
                query,
                output_payload(
                    "search",
                    {
                        "temperature": parameter("temperature", t_min, t_max, t_unit),
                        "density": parameter("density", d_min, d_max, d_unit),
                    },
                    [keyword],
                    "recent",
                    0.97,
                ),
            )
            index += 1

            query = (
                f"find {keyword} experiments where Te is {fmt(t_min)}-{fmt(t_max)} {t_unit} "
                f"and ne is {fmt(d_min)}-{fmt(d_max)} {d_unit}"
            )
            yield record(
                f"query-parse-{index:05d}",
                query,
                output_payload(
                    "search",
                    {
                        "temperature": parameter("temperature", t_min, t_max, t_unit),
                        "density": parameter("density", d_min, d_max, d_unit),
                    },
                    [keyword],
                    None,
                    0.97,
                ),
            )
            index += 1

    for keyword in KEYWORDS:
        for min_value, max_value, unit in TEMPERATURE_RANGES[:5]:
            for template in [
                "statistics for {keyword} temperature between {min} and {max} {unit}",
                "average temperature in {keyword} papers from {min} to {max} {unit}",
                "summarize {keyword} papers with Te {min}-{max} {unit}",
            ]:
                query = template.format(keyword=keyword, min=fmt(min_value), max=fmt(max_value), unit=unit)
                yield record(
                    f"query-parse-{index:05d}",
                    query,
                    output_payload(
                        "statistics",
                        {"temperature": parameter("temperature", min_value, max_value, unit)},
                        [keyword],
                    ),
                )
                index += 1

        for min_value, max_value, unit in DENSITY_RANGES[:5]:
            for template in [
                "average density in {keyword} papers between {min} and {max} {unit}",
                "statistics for {keyword} density from {min} to {max} {unit}",
                "summarize {keyword} papers with ne {min}-{max} {unit}",
            ]:
                query = template.format(keyword=keyword, min=fmt(min_value), max=fmt(max_value), unit=unit)
                yield record(
                    f"query-parse-{index:05d}",
                    query,
                    output_payload(
                        "statistics",
                        {"density": parameter("density", min_value, max_value, unit)},
                        [keyword],
                    ),
                )
                index += 1


def write_splits(
    records: Iterable[Dict],
    output_dir: Path,
    dev_percent: int,
    test_percent: int,
    max_examples: Optional[int],
) -> Dict[str, int]:
    """Write deterministic train/dev/test JSONL files."""
    selected_records = select_balanced(list(records), max_examples)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "train": output_dir / "train.jsonl",
        "dev": output_dir / "dev.jsonl",
        "test": output_dir / "test.jsonl",
    }
    counts = {split: 0 for split in paths}

    with paths["train"].open("w", encoding="utf-8") as train_handle, paths["dev"].open(
        "w", encoding="utf-8"
    ) as dev_handle, paths["test"].open("w", encoding="utf-8") as test_handle:
        handles = {
            "train": train_handle,
            "dev": dev_handle,
            "test": test_handle,
        }
        for item in selected_records:
            split = split_for_id(item["example_id"], dev_percent, test_percent)
            handles[split].write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
            counts[split] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare query parsing SFT JSONL.")
    parser.add_argument("--output-dir", default="training/data/query_parsing")
    parser.add_argument("--dev-percent", type=int, default=10)
    parser.add_argument("--test-percent", type=int, default=10)
    parser.add_argument(
        "--max-examples",
        type=int,
        default=3000,
        help="Maximum examples to write. Set 0 to write all generated examples.",
    )
    args = parser.parse_args()

    max_examples = args.max_examples if args.max_examples > 0 else None
    counts = write_splits(
        make_examples(),
        Path(args.output_dir),
        args.dev_percent,
        args.test_percent,
        max_examples,
    )
    print(
        "Wrote query parsing SFT splits: "
        f"train={counts['train']}, dev={counts['dev']}, test={counts['test']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
