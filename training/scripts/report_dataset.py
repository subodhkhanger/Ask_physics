#!/usr/bin/env python3
"""
Report basic readiness metrics for Ask Physics training data.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List


def read_jsonl(path: Path) -> Iterable[Dict]:
    """Read JSONL records from disk."""
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def count_lines(path: Path) -> int:
    """Count lines in a text file if it exists."""
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def summarize(labels: List[Dict]) -> Dict:
    """Summarize extraction labels."""
    by_type: Dict[str, int] = {}
    positive = 0
    negative = 0
    total_measurements = 0

    for label in labels:
        measurements = label.get("measurements", [])
        if measurements:
            positive += 1
        else:
            negative += 1
        total_measurements += len(measurements)
        for measurement in measurements:
            measurement_type = measurement.get("type", "unknown")
            by_type[measurement_type] = by_type.get(measurement_type, 0) + 1

    return {
        "total_labels": len(labels),
        "positive_papers": positive,
        "negative_papers": negative,
        "total_measurements": total_measurements,
        "measurements_by_type": by_type,
    }


def render_markdown(summary: Dict, raw_count: int, sft_counts: Dict[str, int]) -> str:
    """Render a compact Markdown report."""
    by_type = summary["measurements_by_type"]
    positive = summary["positive_papers"]
    total = summary["total_labels"]
    positive_rate = (positive / total * 100) if total else 0

    return "\n".join(
        [
            "# Ask Physics QLoRA Dataset Report",
            "",
            "## Counts",
            "",
            f"- Raw paper records: {raw_count}",
            f"- Extraction label records: {total}",
            f"- Positive papers: {positive}",
            f"- Negative papers: {summary['negative_papers']}",
            f"- Positive rate: {positive_rate:.1f}%",
            f"- Total measurements: {summary['total_measurements']}",
            "",
            "## Measurements By Type",
            "",
            f"- Temperature: {by_type.get('temperature', 0)}",
            f"- Density: {by_type.get('density', 0)}",
            "",
            "## SFT Splits",
            "",
            f"- Train: {sft_counts.get('train', 0)}",
            f"- Dev: {sft_counts.get('dev', 0)}",
            f"- Test: {sft_counts.get('test', 0)}",
            "",
            "## Readiness Notes",
            "",
            "- Bronze labels are regex-generated weak labels.",
            "- Silver teacher labels and gold manual review are still required before final training claims.",
            "- QLoRA can start as a smoke test once this report shows enough positive and negative rows.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Report Ask Physics QLoRA dataset readiness.")
    parser.add_argument("--raw", default="training/data/raw/arxiv_metadata.jsonl")
    parser.add_argument("--labels", default="training/data/bronze/regex_labels.jsonl")
    parser.add_argument("--sft-dir", default="training/data/sft")
    parser.add_argument("--output", default="training/reports/dataset_report.md")
    args = parser.parse_args()

    labels = list(read_jsonl(Path(args.labels)))
    summary = summarize(labels)
    raw_count = count_lines(Path(args.raw))
    sft_dir = Path(args.sft_dir)
    sft_counts = {
        "train": count_lines(sft_dir / "train.jsonl"),
        "dev": count_lines(sft_dir / "dev.jsonl"),
        "test": count_lines(sft_dir / "test.jsonl"),
    }

    report = render_markdown(summary, raw_count, sft_counts)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
