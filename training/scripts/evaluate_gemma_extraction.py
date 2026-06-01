#!/usr/bin/env python3
"""
Evaluate Gemma extraction JSON quality and coarse measurement matching.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from run_gemma_inference import build_messages, generate, load_config, load_model


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """Read JSONL records."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract a JSON object from model text."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def measurement_types(payload: Dict[str, Any]) -> List[str]:
    """Return measurement type labels from an extraction payload."""
    measurements = payload.get("measurements", [])
    if not isinstance(measurements, list):
        return []
    return [
        item.get("type")
        for item in measurements
        if isinstance(item, dict) and item.get("type") in {"temperature", "density"}
    ]


def assistant_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Load the gold/expected assistant JSON from an SFT record."""
    return json.loads(record["messages"][-1]["content"])


def score_types(expected: List[str], predicted: List[str]) -> Dict[str, int]:
    """Score coarse type-level true/false positives and false negatives."""
    expected_counts = {item: expected.count(item) for item in set(expected)}
    predicted_counts = {item: predicted.count(item) for item in set(predicted)}
    tp = 0
    fp = 0
    fn = 0
    for label in {"temperature", "density"}:
        tp += min(expected_counts.get(label, 0), predicted_counts.get(label, 0))
        fp += max(0, predicted_counts.get(label, 0) - expected_counts.get(label, 0))
        fn += max(0, expected_counts.get(label, 0) - predicted_counts.get(label, 0))
    return {"tp": tp, "fp": fp, "fn": fn}


def precision_recall_f1(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """Compute precision/recall/F1."""
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate(args: argparse.Namespace) -> Dict[str, Any]:
    """Run model evaluation over an SFT JSONL file."""
    config = load_config(Path(args.config))
    generation = config.get("generation", {})
    model, tokenizer = load_model(config, args.adapter_dir)
    records = list(read_jsonl(Path(args.eval_file)))
    if args.limit:
        records = records[: args.limit]

    valid_json = 0
    schema_valid = 0
    type_scores = {"tp": 0, "fp": 0, "fn": 0}
    rows = []

    for index, record in enumerate(records, start=1):
        system = record["messages"][0]
        user = record["messages"][1]
        title = user["content"].split("\nAbstract:", 1)[0].replace("Title: ", "")
        abstract = user["content"].split("\nAbstract:", 1)[1]
        text = generate(
            model,
            tokenizer,
            [system, *build_messages(title, abstract)[1:]],
            max_new_tokens=int(generation.get("max_new_tokens", 512)),
            temperature=float(generation.get("temperature", 0.0)),
            top_p=float(generation.get("top_p", 1.0)),
        )
        predicted_payload = extract_json(text)
        expected_payload = assistant_payload(record)
        row = {
            "paper_id": record["paper_id"],
            "raw_prediction": text,
            "expected": expected_payload,
            "predicted": predicted_payload,
        }
        if predicted_payload is not None:
            valid_json += 1
            if isinstance(predicted_payload.get("measurements"), list):
                schema_valid += 1
                scores = score_types(
                    measurement_types(expected_payload),
                    measurement_types(predicted_payload),
                )
                for key, value in scores.items():
                    type_scores[key] += value
        rows.append(row)
        if index % 10 == 0:
            print(f"evaluated {index}/{len(records)}")

    metrics = {
        "records": len(records),
        "valid_json_rate": valid_json / len(records) if records else 0.0,
        "schema_valid_rate": schema_valid / len(records) if records else 0.0,
        "type_match": {
            **type_scores,
            **precision_recall_f1(type_scores["tp"], type_scores["fp"], type_scores["fn"]),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump({"metrics": metrics, "rows": rows}, handle, indent=2, sort_keys=True)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Gemma QLoRA extraction.")
    parser.add_argument("--config", default="training/configs/gemma_qlora.yaml")
    parser.add_argument("--adapter-dir", default="training/runs/gemma-qlora-ask-physics/adapter")
    parser.add_argument("--eval-file", default="training/data/sft_balanced/test.jsonl")
    parser.add_argument("--output", default="training/runs/gemma-qlora-ask-physics/eval_predictions.json")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    metrics = evaluate(args)
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
