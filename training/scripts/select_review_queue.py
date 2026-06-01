#!/usr/bin/env python3
"""
Select a balanced manual-review queue from bronze labels.

The output is not gold data yet. It is a queue for human review. After review,
the corrected rows can become the gold evaluation set.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def read_jsonl(path: Path) -> Iterable[Dict]:
    """Read JSONL records from disk."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def stable_sort_key(record: Dict) -> str:
    """Return a deterministic pseudo-random sort key."""
    return hashlib.sha256(record["paper_id"].encode("utf-8")).hexdigest()


def has_type(record: Dict, measurement_type: str) -> bool:
    """Return whether a label contains a measurement type."""
    return any(item.get("type") == measurement_type for item in record.get("measurements", []))


def add_review_fields(record: Dict, bucket: str) -> Dict:
    """Add fields needed for manual review without changing the label payload."""
    review_record = dict(record)
    review_record["review"] = {
        "bucket": bucket,
        "status": "pending",
        "is_correct": None,
        "corrected_measurements": None,
        "reviewer_notes": None,
    }
    return review_record


def take(records: List[Dict], count: int, bucket: str) -> List[Dict]:
    """Take a deterministic sample from a bucket."""
    return [add_review_fields(record, bucket) for record in sorted(records, key=stable_sort_key)[:count]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Select a balanced gold-review queue.")
    parser.add_argument("--labels", default="training/data/bronze/regex_labels.jsonl")
    parser.add_argument("--output", default="training/data/gold/review_queue.jsonl")
    parser.add_argument("--density", type=int, default=100)
    parser.add_argument("--temperature", type=int, default=120)
    parser.add_argument("--negative", type=int, default=80)
    args = parser.parse_args()

    labels = list(read_jsonl(Path(args.labels)))
    density = [record for record in labels if has_type(record, "density")]
    temperature_only = [
        record for record in labels
        if has_type(record, "temperature") and not has_type(record, "density")
    ]
    negative = [record for record in labels if not record.get("measurements")]

    queue = []
    queue.extend(take(density, args.density, "density_positive"))
    queue.extend(take(temperature_only, args.temperature, "temperature_positive"))
    queue.extend(take(negative, args.negative, "negative"))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in queue:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(
        f"Wrote {len(queue)} review rows to {output} "
        f"(density={min(len(density), args.density)}, "
        f"temperature={min(len(temperature_only), args.temperature)}, "
        f"negative={min(len(negative), args.negative)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
