#!/usr/bin/env python3
"""
Collect arXiv metadata for the Ask Physics QLoRA data pipeline.

This script writes JSONL so large collections can be streamed, diffed, and
validated without loading the whole dataset at once.
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


DEFAULT_QUERIES = [
    "cat:physics.plasm-ph",
    "all:tokamak",
    "all:stellarator",
    'all:"fusion plasma"',
    'all:"electron temperature"',
    'all:"electron density"',
    'all:"plasma density"',
]


def clean_text(value: str) -> str:
    """Collapse arXiv whitespace into a stable single-line string."""
    return " ".join(value.split())


def arxiv_id_from_entry(entry_id: str) -> str:
    """Convert an arXiv entry URL into a stable arXiv ID."""
    return entry_id.rstrip("/").split("/")[-1]


def result_to_record(result: object, query: str) -> Dict:
    """Convert an arXiv API result into the raw paper metadata schema."""
    arxiv_id = arxiv_id_from_entry(result.entry_id)
    primary_category = getattr(result, "primary_category", None)

    return {
        "schema_version": "paper_metadata.v1",
        "paper_id": f"arxiv:{arxiv_id}",
        "arxiv_id": arxiv_id,
        "title": clean_text(result.title),
        "abstract": clean_text(result.summary),
        "authors": [author.name for author in result.authors],
        "published": result.published.isoformat() if result.published else None,
        "updated": result.updated.isoformat() if result.updated else None,
        "categories": list(result.categories or []),
        "primary_category": primary_category,
        "source_url": f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": result.pdf_url,
        "comment": result.comment,
        "journal_ref": result.journal_ref,
        "doi": result.doi,
        "provenance": {
            "source": "arxiv",
            "query": query,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def collect_query(query: str, max_results: int, delay_seconds: float) -> Iterable[Dict]:
    """Yield raw metadata records for one arXiv query."""
    try:
        import arxiv
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: arxiv. Install with "
            "`python3 -m pip install -r training/requirements.txt`."
        ) from exc

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    client = arxiv.Client(
        page_size=min(max_results, 100),
        delay_seconds=delay_seconds,
        num_retries=3,
    )

    for result in client.results(search):
        yield result_to_record(result, query)


def write_jsonl(records: List[Dict], output_path: Path) -> None:
    """Write records as UTF-8 JSONL."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def parse_queries(args: argparse.Namespace) -> List[str]:
    """Resolve CLI query input into an ordered query list."""
    queries = list(args.query or [])
    if args.query_file:
        query_file = Path(args.query_file)
        queries.extend(
            line.strip()
            for line in query_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    return queries or DEFAULT_QUERIES


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect arXiv metadata for QLoRA data preparation.")
    parser.add_argument(
        "--query",
        action="append",
        help="arXiv query to collect. Can be supplied multiple times.",
    )
    parser.add_argument(
        "--query-file",
        help="Optional file containing one arXiv query per line.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=25,
        help="Maximum results per query.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.5,
        help="Delay between arXiv records to avoid aggressive API use.",
    )
    parser.add_argument(
        "--output",
        default="training/data/raw/arxiv_metadata.jsonl",
        help="Output JSONL path.",
    )
    args = parser.parse_args()

    seen = set()
    records: List[Dict] = []
    queries = parse_queries(args)

    print(f"Collecting up to {args.max_results} records for each of {len(queries)} queries")
    for query in queries:
        print(f"- {query}", flush=True)
        query_count = 0
        for record in collect_query(query, args.max_results, args.delay_seconds):
            query_count += 1
            if record["paper_id"] in seen:
                continue
            seen.add(record["paper_id"])
            records.append(record)
            if len(records) % 50 == 0:
                write_jsonl(records, Path(args.output))
                print(f"  saved {len(records)} deduplicated records", flush=True)
        print(f"  query returned {query_count} records; corpus size is {len(records)}", flush=True)

    output_path = Path(args.output)
    write_jsonl(records, output_path)

    print(f"Wrote {len(records)} deduplicated records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
