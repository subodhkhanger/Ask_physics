#!/usr/bin/env python3
"""
Convert extraction labels into model-neutral SFT chat JSONL.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


SYSTEM_PROMPT = (
    "Extract plasma physics measurements from paper titles and abstracts. "
    "Return only valid JSON with a top-level measurements array. "
    "Each measurement must include type, value, unit, normalized_value, "
    "normalized_unit, context, and confidence. Return an empty array when "
    "no temperature or density measurement is present."
)


def read_jsonl(path: Path) -> Iterable[Dict]:
    """Read JSONL records from disk."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def split_for_paper(paper_id: str, dev_percent: int, test_percent: int) -> str:
    """Assign a deterministic split from the paper ID hash."""
    bucket = int(hashlib.sha256(paper_id.encode("utf-8")).hexdigest(), 16) % 100
    if bucket < test_percent:
        return "test"
    if bucket < test_percent + dev_percent:
        return "dev"
    return "train"


def assistant_payload(label: Dict) -> str:
    """Build strict JSON assistant output for SFT."""
    payload = {"measurements": label.get("measurements", [])}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_sft_record(label: Dict) -> Dict:
    """Convert one extraction label into one chat SFT record."""
    user_content = f"Title: {label['title']}\nAbstract: {label['abstract']}"
    return {
        "schema_version": "sft_chat.v1",
        "paper_id": label["paper_id"],
        "task": "abstract_measurement_extraction",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_payload(label)},
        ],
    }


def write_splits(records: Iterable[Dict], output_dir: Path, dev_percent: int, test_percent: int) -> Dict[str, int]:
    """Write deterministic train/dev/test JSONL files."""
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
        for record in records:
            split = split_for_paper(record["paper_id"], dev_percent, test_percent)
            handles[split].write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            counts[split] += 1

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare model-neutral SFT JSONL from extraction labels.")
    parser.add_argument(
        "--labels",
        default="training/data/bronze/regex_labels.jsonl",
        help="Extraction label JSONL.",
    )
    parser.add_argument(
        "--output-dir",
        default="training/data/sft",
        help="Output directory for train/dev/test JSONL.",
    )
    parser.add_argument(
        "--dev-percent",
        type=int,
        default=10,
        help="Percent of paper IDs assigned to dev.",
    )
    parser.add_argument(
        "--test-percent",
        type=int,
        default=10,
        help="Percent of paper IDs assigned to test.",
    )
    args = parser.parse_args()

    records = (build_sft_record(label) for label in read_jsonl(Path(args.labels)))
    counts = write_splits(records, Path(args.output_dir), args.dev_percent, args.test_percent)

    print(
        "Wrote SFT splits: "
        f"train={counts['train']}, dev={counts['dev']}, test={counts['test']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
