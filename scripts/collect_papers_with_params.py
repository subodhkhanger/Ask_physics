"""
Collect plasma physics papers that likely contain experimental parameters.

Strategy: Look for papers with keywords indicating experimental measurements.
"""

import arxiv
import json
from pathlib import Path
from datetime import datetime
import time
import re


def has_likely_parameters(abstract: str) -> bool:
    """Check if abstract likely contains temperature or density measurements."""
    # Look for patterns suggesting experimental measurements
    patterns = [
        r'\d+\.?\d*\s*(keV|eV|K)',  # Temperature with units
        r'\d+\.?\d*\s*[×x]\s*10\^?\d+\s*(m\^?-?3|cm\^?-?3)',  # Density
        r'temperature.*\d+',  # Temperature followed by number
        r'density.*\d+',  # Density followed by number
        r'(measured|observed|achieved|reached).*\d+',  # Measurement language
        r'experimental.*\d+',  # Experimental results
        r'tokamak|plasma|discharge|confinement',  # Tokamak-related
    ]

    for pattern in patterns:
        if re.search(pattern, abstract, re.IGNORECASE):
            return True
    return False


def collect_papers_with_filters(
    n: int = 50,
    save_path: str = "data/papers_filtered.json",
    category: str = "physics.plasm-ph"
):
    """
    Collect papers and filter for those likely to have parameters.
    """
    print(f"Searching for {n} papers with experimental parameters...")
    print("(This may take a while as we're filtering results)")

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)

    # Search for more papers than needed to have filtering buffer
    search = arxiv.Search(
        query=f"cat:{category} AND (temperature OR density OR experimental OR tokamak OR plasma)",
        max_results=n * 3,  # Collect 3x to account for filtering
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    papers = []
    papers_checked = 0

    try:
        for result in search.results():
            papers_checked += 1
            abstract = result.summary.replace('\n', ' ')

            # Check if likely to have parameters
            if has_likely_parameters(abstract):
                paper = {
                    'id': result.entry_id.split('/')[-1],
                    'title': result.title,
                    'abstract': abstract,
                    'authors': [author.name for author in result.authors],
                    'published': result.published.isoformat(),
                    'pdf_url': result.pdf_url,
                    'categories': result.categories,
                    'collected_at': datetime.now().isoformat()
                }
                papers.append(paper)

                print(f"  [{len(papers)}/{n}] Found: {paper['id']}")

                if len(papers) >= n:
                    break

                time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n! Collection interrupted by user")

    # Save results
    if papers:
        with open(save_path, 'w') as f:
            json.dump(papers, f, indent=2)

        print(f"\n✓ Collected {len(papers)} papers (checked {papers_checked} total)")
        print(f"✓ Saved to: {save_path}")
        print(f"\nFiltering effectiveness: {len(papers)/papers_checked*100:.1f}% of papers had keywords")

        return papers
    else:
        print("! No papers found")
        return []


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect papers filtered for experimental parameters"
    )
    parser.add_argument('--limit', type=int, default=20, help='Number of papers to collect')
    parser.add_argument('--output', type=str, default='data/papers_filtered.json', help='Output file')

    args = parser.parse_args()

    papers = collect_papers_with_filters(n=args.limit, save_path=args.output)

    if papers:
        print("\n✓ Ready for extraction:")
        print(f"  python scripts/extract_parameters.py --input {args.output}")
