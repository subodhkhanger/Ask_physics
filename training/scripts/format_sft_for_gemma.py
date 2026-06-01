#!/usr/bin/env python3
"""
Format Ask Physics model-neutral SFT JSONL for Gemma QLoRA training.

Input records look like:

{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "{\"measurements\": [...]}"}
  ]
}

Output records keep metadata and add a single `text` field rendered with the
Gemma tokenizer chat template. That `text` field is what QLoRA trains on.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List

from transformers import AutoTokenizer


def read_jsonl(path: Path) -> Iterable[Dict]:
    """Read JSONL records from disk."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(records: Iterable[Dict], path: Path) -> int:
    """Write JSONL records and return count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def render_messages(tokenizer: AutoTokenizer, messages: List[Dict[str, str]]) -> str:
    """Render messages with the Gemma tokenizer chat template."""
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )


def format_record(tokenizer: AutoTokenizer, record: Dict) -> Dict:
    """Convert one model-neutral SFT record into one Gemma text record."""
    return {
        "schema_version": "gemma_sft_text.v1",
        "source_schema_version": record.get("schema_version"),
        "paper_id": record["paper_id"],
        "task": record["task"],
        "text": render_messages(tokenizer, record["messages"]),
    }


def format_file(tokenizer: AutoTokenizer, input_path: Path, output_path: Path) -> int:
    """Format one split file."""
    records = (format_record(tokenizer, record) for record in read_jsonl(input_path))
    return write_jsonl(records, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Format Ask Physics SFT JSONL for Gemma.")
    parser.add_argument(
        "--model",
        default="google/gemma-2-2b-it",
        help="Gemma tokenizer/model ID.",
    )
    parser.add_argument(
        "--input-dir",
        default="training/data/sft_balanced",
        help="Directory containing train/dev/test model-neutral SFT JSONL.",
    )
    parser.add_argument(
        "--output-dir",
        default="training/data/gemma_sft_balanced",
        help="Output directory for Gemma-formatted train/dev/test JSONL.",
    )
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    split_map = {
        "train": ("train.jsonl", "train.jsonl"),
        "dev": ("dev.jsonl", "dev.jsonl"),
        "test": ("test.jsonl", "test.jsonl"),
    }

    for split, (input_name, output_name) in split_map.items():
        count = format_file(
            tokenizer,
            input_dir / input_name,
            output_dir / output_name,
        )
        print(f"formatted {split}: {count} records -> {output_dir / output_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
