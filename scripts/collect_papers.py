"""
Collect plasma physics papers from arXiv.

Following SKILLS.md best practices:
- Start with small batch (10 papers) for validation
- Save incrementally to handle network failures
- Include all relevant metadata
"""

import arxiv
import json
import argparse
from pathlib import Path
from datetime import datetime
import time


def collect_plasma_physics_papers(
    n: int = 10,
    save_path: str = "data/papers.json",
    category: str = "physics.plasm-ph"
):
    """
    Collect recent plasma physics papers from arXiv.

    Args:
        n: Number of papers to collect
        save_path: Path to save JSON file
        category: arXiv category (default: physics.plasm-ph for plasma physics)

    Best practices:
    - Sort by SubmittedDate for most recent papers
    - Include published date for filtering
    - Save incrementally (API can be flaky)
    - Add retry logic with exponential backoff
    """
    print(f"Collecting {n} papers from arXiv category: {category}")

    # Create data directory if it doesn't exist
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    # Configure search
    search = arxiv.Search(
        query=f"cat:{category}",  # Plasma physics category
        max_results=n,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    papers = []
    retry_count = 0
    max_retries = 3

    try:
        for i, result in enumerate(search.results()):
            try:
                paper = {
                    'id': result.entry_id.split('/')[-1],  # Extract arxiv ID
                    'title': result.title,
                    'abstract': result.summary.replace('\n', ' '),  # Clean whitespace
                    'authors': [author.name for author in result.authors],
                    'published': result.published.isoformat(),
                    'pdf_url': result.pdf_url,
                    'categories': result.categories,
                    'collected_at': datetime.now().isoformat()
                }
                papers.append(paper)

                print(f"  [{i+1}/{n}] {paper['id']}: {paper['title'][:60]}...")

                # Save incrementally every 10 papers (adjusted for small batches)
                if (i + 1) % min(10, n) == 0:
                    with open(save_path, 'w') as f:
                        json.dump(papers, f, indent=2)
                    print(f"  ✓ Saved {i + 1} papers to {save_path}")

                # Small delay to be respectful to arXiv API
                time.sleep(0.5)

            except Exception as e:
                print(f"  ✗ Error processing paper {i+1}: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"  ! Max retries reached, skipping...")
                    continue
                time.sleep(2 ** retry_count)  # Exponential backoff

    except KeyboardInterrupt:
        print("\n! Collection interrupted by user")

    # Final save
    if papers:
        with open(save_path, 'w') as f:
            json.dump(papers, f, indent=2)
        print(f"\n✓ Final save: {len(papers)} papers saved to {save_path}")

        # Print summary statistics
        print("\n=== Collection Summary ===")
        print(f"Total papers collected: {len(papers)}")
        print(f"Date range: {papers[-1]['published'][:10]} to {papers[0]['published'][:10]}")
        print(f"Average abstract length: {sum(len(p['abstract']) for p in papers) / len(papers):.0f} chars")

        return papers
    else:
        print("! No papers collected")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Collect plasma physics papers from arXiv"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of papers to collect (default: 10, recommend starting small)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/papers.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--category',
        type=str,
        default='physics.plasm-ph',
        help='arXiv category to search (default: physics.plasm-ph)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Phase 1: Data Collection")
    print("=" * 60)
    print(f"Following SKILLS.md guidance: Starting with {args.limit} papers")
    print("✓ Will validate extraction accuracy before scaling up")
    print()

    papers = collect_plasma_physics_papers(
        n=args.limit,
        save_path=args.output,
        category=args.category
    )

    if papers:
        print(f"\n✓ Success! Ready for parameter extraction.")
        print(f"  Next: python scripts/extract_parameters.py --input {args.output}")
    else:
        print("\n✗ Failed to collect papers. Check your internet connection.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
