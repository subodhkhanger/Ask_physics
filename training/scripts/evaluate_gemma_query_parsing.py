#!/usr/bin/env python3
"""
Evaluate Gemma query parsing JSON quality and coarse parser accuracy.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from run_gemma_inference import generate, load_config, load_model


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


def expected_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Load expected assistant JSON from an SFT record."""
    return json.loads(record["messages"][-1]["content"])


def parameter_keys(payload: Optional[Dict[str, Any]]) -> set[str]:
    """Return top-level parameter names."""
    if not payload or not isinstance(payload.get("parameters"), dict):
        return set()
    return set(payload["parameters"].keys())


def keyword_overlap(expected: Dict[str, Any], predicted: Optional[Dict[str, Any]]) -> Dict[str, int]:
    """Score keyword set overlap."""
    expected_keywords = set(expected.get("keywords", []))
    predicted_keywords = set(predicted.get("keywords", [])) if predicted else set()
    return {
        "tp": len(expected_keywords & predicted_keywords),
        "fp": len(predicted_keywords - expected_keywords),
        "fn": len(expected_keywords - predicted_keywords),
    }


def precision_recall_f1(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """Compute precision/recall/F1."""
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def evaluate(args: argparse.Namespace) -> Dict[str, Any]:
    """Run model evaluation over a query parsing SFT JSONL file."""
    config = load_config(Path(args.config))
    generation = config.get("generation", {})
    model, processor, tokenizer = load_model(config, args.adapter_dir)
    records = list(read_jsonl(Path(args.eval_file)))
    if args.limit:
        records = records[: args.limit]

    valid_json = 0
    schema_valid = 0
    intent_correct = 0
    temporal_correct = 0
    parameter_scores = {"tp": 0, "fp": 0, "fn": 0}
    keyword_scores = {"tp": 0, "fp": 0, "fn": 0}
    rows = []

    for index, record in enumerate(records, start=1):
        messages = record["messages"][:2]
        text = generate(
            model,
            processor,
            tokenizer,
            messages,
            max_new_tokens=int(generation.get("max_new_tokens", 256)),
            temperature=float(generation.get("temperature", 0.0)),
            top_p=float(generation.get("top_p", 1.0)),
        )
        predicted = extract_json(text)
        expected = expected_payload(record)

        if predicted is not None:
            valid_json += 1
            required = {"intent", "parameters", "keywords", "temporal_constraint", "confidence"}
            if required.issubset(predicted.keys()) and isinstance(predicted.get("parameters"), dict):
                schema_valid += 1
            if predicted.get("intent") == expected.get("intent"):
                intent_correct += 1
            if predicted.get("temporal_constraint") == expected.get("temporal_constraint"):
                temporal_correct += 1

        expected_params = parameter_keys(expected)
        predicted_params = parameter_keys(predicted)
        parameter_scores["tp"] += len(expected_params & predicted_params)
        parameter_scores["fp"] += len(predicted_params - expected_params)
        parameter_scores["fn"] += len(expected_params - predicted_params)

        scores = keyword_overlap(expected, predicted)
        for key, value in scores.items():
            keyword_scores[key] += value

        rows.append(
            {
                "example_id": record.get("example_id"),
                "query": messages[1]["content"],
                "raw_prediction": text,
                "expected": expected,
                "predicted": predicted,
            }
        )
        if index % 25 == 0:
            print(f"evaluated {index}/{len(records)}")

    total = len(records)
    metrics = {
        "records": total,
        "valid_json_rate": valid_json / total if total else 0.0,
        "schema_valid_rate": schema_valid / total if total else 0.0,
        "intent_accuracy": intent_correct / total if total else 0.0,
        "temporal_accuracy": temporal_correct / total if total else 0.0,
        "parameter_key_match": {
            **parameter_scores,
            **precision_recall_f1(parameter_scores["tp"], parameter_scores["fp"], parameter_scores["fn"]),
        },
        "keyword_match": {
            **keyword_scores,
            **precision_recall_f1(keyword_scores["tp"], keyword_scores["fp"], keyword_scores["fn"]),
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump({"metrics": metrics, "rows": rows}, handle, indent=2, sort_keys=True)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Gemma QLoRA query parsing.")
    parser.add_argument("--config", default="training/configs/gemma_query_parsing_qlora.yaml")
    parser.add_argument("--adapter-dir", default="training/runs/gemma-query-parsing-qlora/adapter")
    parser.add_argument("--eval-file", default="training/data/query_parsing/test.jsonl")
    parser.add_argument("--output", default="training/runs/gemma-query-parsing-qlora/eval_predictions.json")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    metrics = evaluate(args)
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
