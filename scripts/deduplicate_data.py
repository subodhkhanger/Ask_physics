"""
Remove duplicate entries from data files.

This script removes:
1. Duplicate parameter values within the same paper in extracted_with_llm.json
2. Duplicate papers in papers.json (if any)
3. Duplicate measurements in plasma_data.ttl

Usage:
    python scripts/deduplicate_data.py
    python scripts/deduplicate_data.py --dry-run  # Preview changes without saving
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import argparse


def deduplicate_extracted_params(input_file: str, output_file: str, dry_run: bool = False):
    """
    Remove duplicate parameters within each paper.

    Two parameters are considered duplicates if they have:
    - Same value
    - Same unit
    - Similar context (optional)
    """
    print(f"\n{'=' * 60}")
    print(f"Deduplicating extracted parameters: {input_file}")
    print(f"{'=' * 60}")

    with open(input_file, 'r') as f:
        data = json.load(f)

    total_before_temps = 0
    total_before_dens = 0
    total_after_temps = 0
    total_after_dens = 0
    papers_modified = 0

    for entry in data:
        # Process temperatures
        temps_before = len(entry['parameters']['temperature'])
        unique_temps = []
        seen = set()

        for temp in entry['parameters']['temperature']:
            # Create a key for deduplication (value + unit)
            key = (temp['value'], temp['unit'])
            if key not in seen:
                seen.add(key)
                unique_temps.append(temp)

        # Process densities
        dens_before = len(entry['parameters']['density'])
        unique_dens = []
        seen = set()

        for dens in entry['parameters']['density']:
            # Create a key for deduplication (value + unit)
            key = (dens['value'], dens['unit'])
            if key not in seen:
                seen.add(key)
                unique_dens.append(dens)

        # Update statistics
        total_before_temps += temps_before
        total_before_dens += dens_before
        total_after_temps += len(unique_temps)
        total_after_dens += len(unique_dens)

        # Update entry
        if temps_before != len(unique_temps) or dens_before != len(unique_dens):
            papers_modified += 1
            print(f"  {entry['paper_id']}:")
            if temps_before != len(unique_temps):
                print(f"    Temperatures: {temps_before} -> {len(unique_temps)}")
            if dens_before != len(unique_dens):
                print(f"    Densities: {dens_before} -> {len(unique_dens)}")

        entry['parameters']['temperature'] = unique_temps
        entry['parameters']['density'] = unique_dens

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"{'=' * 60}")
    print(f"Papers modified: {papers_modified}/{len(data)}")
    print(f"Temperatures: {total_before_temps} -> {total_after_temps} (removed {total_before_temps - total_after_temps})")
    print(f"Densities: {total_before_dens} -> {total_after_dens} (removed {total_before_dens - total_after_dens})")

    if not dry_run:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved to: {output_file}")
    else:
        print("\nDRY RUN - No files modified")

    return data


def deduplicate_papers(input_file: str, output_file: str, dry_run: bool = False):
    """
    Remove duplicate papers based on paper ID.
    Keep the most recent version if duplicates exist.
    """
    print(f"\n{'=' * 60}")
    print(f"Deduplicating papers: {input_file}")
    print(f"{'=' * 60}")

    with open(input_file, 'r') as f:
        papers = json.load(f)

    # Track papers by ID, keeping the most recently collected
    papers_by_id = {}
    duplicates_found = 0

    for paper in papers:
        paper_id = paper['id']
        if paper_id in papers_by_id:
            duplicates_found += 1
            # Keep the more recently collected version
            existing_date = papers_by_id[paper_id].get('collected_at', '')
            new_date = paper.get('collected_at', '')
            if new_date > existing_date:
                print(f"  Replacing {paper_id} with newer version")
                papers_by_id[paper_id] = paper
            else:
                print(f"  Keeping existing {paper_id}")
        else:
            papers_by_id[paper_id] = paper

    unique_papers = list(papers_by_id.values())

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"{'=' * 60}")
    print(f"Papers before: {len(papers)}")
    print(f"Papers after: {len(unique_papers)}")
    print(f"Duplicates removed: {duplicates_found}")

    if not dry_run:
        with open(output_file, 'w') as f:
            json.dump(unique_papers, f, indent=2)
        print(f"\nSaved to: {output_file}")
    else:
        print("\nDRY RUN - No files modified")

    return unique_papers


def deduplicate_ttl(input_file: str, output_file: str, dry_run: bool = False):
    """
    Remove duplicate measurements from TTL file.
    Two measurements are duplicates if they measure the same parameter value.
    """
    print(f"\n{'=' * 60}")
    print(f"Deduplicating TTL data: {input_file}")
    print(f"{'=' * 60}")

    with open(input_file, 'r') as f:
        content = f.read()

    # Parse TTL to find measurements and parameters
    # Track parameter URIs that are already used
    seen_params = set()
    lines_to_keep = []
    measurement_pattern = re.compile(r'<http://example.org/plasma/measurement/m\d+>')
    param_pattern = re.compile(r'<http://example.org/plasma/parameter/p(\d+)>')

    current_block = []
    skip_block = False
    params_before = 0
    params_after = 0

    for line in content.split('\n'):
        # Check if this is a parameter definition
        param_match = param_pattern.search(line)

        if param_match and 'a :' in line:
            # New parameter block starting
            param_id = param_match.group(1)
            params_before += 1

            # We'll need to look ahead to see the value
            # For now, just collect the block
            current_block = [line]
            continue
        elif current_block:
            # We're in a parameter block
            current_block.append(line)

            # Check if block is complete (ends with . or empty line)
            if line.strip().endswith('.') or line.strip() == '':
                # Extract value and unit from block
                block_text = '\n'.join(current_block)
                value_match = re.search(r':value\s+([\d.e+-]+)', block_text)
                unit_match = re.search(r':unitString\s+"([^"]+)"', block_text)

                if value_match and unit_match:
                    key = (float(value_match.group(1)), unit_match.group(1))
                    if key not in seen_params:
                        seen_params.add(key)
                        lines_to_keep.extend(current_block)
                        params_after += 1
                    else:
                        # Skip this duplicate parameter block
                        pass
                else:
                    # Keep block if we can't parse it
                    lines_to_keep.extend(current_block)
                    params_after += 1

                current_block = []
            continue
        else:
            # Regular line, keep it
            lines_to_keep.append(line)

    new_content = '\n'.join(lines_to_keep)

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"{'=' * 60}")
    print(f"Parameters before: ~{params_before}")
    print(f"Parameters after: ~{params_after}")
    print(f"Duplicates removed: ~{params_before - params_after}")

    if not dry_run:
        with open(output_file, 'w') as f:
            f.write(new_content)
        print(f"\nSaved to: {output_file}")
    else:
        print("\nDRY RUN - No files modified")


def main():
    parser = argparse.ArgumentParser(
        description="Remove duplicate entries from data files"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        default=True,
        help='Create backup files before modifying (default: True)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backups'
    )

    args = parser.parse_args()

    # Handle backup flags
    create_backup = args.backup and not args.no_backup

    print("=" * 60)
    print("Data Deduplication Script")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Backup: {'Yes' if create_backup else 'No'}")

    # File paths
    data_dir = Path('data')

    files = {
        'extracted': data_dir / 'extracted_with_llm.json',
        'papers': data_dir / 'papers.json',
        'ttl': data_dir / 'plasma_data.ttl'
    }

    # Create backups if requested
    if create_backup and not args.dry_run:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for name, filepath in files.items():
            if filepath.exists():
                backup_path = filepath.parent / f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
                import shutil
                shutil.copy2(filepath, backup_path)
                print(f"Backup created: {backup_path}")

    # Deduplicate extracted parameters
    if files['extracted'].exists():
        deduplicate_extracted_params(
            str(files['extracted']),
            str(files['extracted']),
            args.dry_run
        )
    else:
        print(f"\nSkipping {files['extracted']} (not found)")

    # Deduplicate papers
    if files['papers'].exists():
        deduplicate_papers(
            str(files['papers']),
            str(files['papers']),
            args.dry_run
        )
    else:
        print(f"\nSkipping {files['papers']} (not found)")

    # Deduplicate TTL (commented out for now as it needs more sophisticated parsing)
    # if files['ttl'].exists():
    #     deduplicate_ttl(
    #         str(files['ttl']),
    #         str(files['ttl']),
    #         args.dry_run
    #     )
    # else:
    #     print(f"\nSkipping {files['ttl']} (not found)")

    print("\n" + "=" * 60)
    print("Deduplication Complete!")
    print("=" * 60)

    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\nData files have been deduplicated.")
        print("\nNext steps:")
        print("  1. Review the changes")
        print("  2. Regenerate the TTL file: python scripts/build_knowledge_graph.py")


if __name__ == "__main__":
    main()
