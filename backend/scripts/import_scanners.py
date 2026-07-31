#!/usr/bin/env python3
"""
Batch import batch-1 scanners from MASTER_LIST.md into the mapping-db API.

Reads each scanner row from the "批次 1: 扫描器/检测工具" section,
extracts name/URL/methodology, and POSTs to /api/sources.

Usage:
    python scripts/import_scanners.py [--api-url http://localhost:8000]
"""

import argparse
import re
import sys
from pathlib import Path

import httpx

# Path to MASTER_LIST.md relative to the project root
DEFAULT_LIST_PATH = Path(__file__).resolve().parents[2] / "hermes-work" / "taxonomy-sources" / "MASTER_LIST.md"


def parse_master_list(path: Path) -> list[dict]:
    """Parse batch-1 scanner rows from MASTER_LIST.md markdown table."""
    text = path.read_text(encoding="utf-8")

    # Find the batch-1 section: "## 批次 1: 扫描器/检测工具"
    batch1_start = text.find("## 批次 1: 扫描器/检测工具")
    if batch1_start == -1:
        print("ERROR: Could not find batch-1 section header", file=sys.stderr)
        return []

    # Find the next section header to bound batch-1
    after_batch1 = text[batch1_start:]
    next_section = re.search(r"\n## ", after_batch1[10:])  # skip the header itself
    if next_section:
        batch1_text = after_batch1[: next_section.start() + 10]
    else:
        batch1_text = after_batch1

    # Parse markdown table rows
    # Format: | # | Name | URL | 核心方法论 | Status |
    scanners = []
    for line in batch1_text.splitlines():
        # Skip header/separator lines and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith("|#") or stripped.startswith("|---"):
            continue
        if not stripped.startswith("|"):
            continue

        # Split by | and strip each cell
        cells = [c.strip() for c in stripped.split("|")]
        # cells: ['', '#', 'Name', 'URL', '方法论', 'Status', '']
        if len(cells) < 7:
            continue

        num = cells[1]
        name = cells[2]
        url = cells[3]
        methodology = cells[4]
        # status = cells[5]  # predominantly ignored for import

        # Skip non-data rows (header rows, etc.)
        if num == "#" or not num.isdigit():
            continue

        # Clean name: remove bold markers and any parenthetical notes
        clean_name = re.sub(r"\*\*([^*]+)\*\*", r"\1", name)
        clean_name = re.sub(r"\s*⚠️.*$", "", clean_name).strip()

        # Build notes from methodology
        notes = methodology if methodology else None

        scanners.append({
            "name": clean_name,
            "source_type": "scanner",
            "url": url if url else None,
            "notes": notes,
        })

    return scanners


async def import_scanners(api_url: str, scanners: list[dict]) -> int:
    """POST each scanner as a source. Returns count of successfully created sources."""
    created = 0
    async with httpx.AsyncClient(base_url=api_url, timeout=30.0) as client:
        for s in scanners:
            try:
                resp = await client.post("/api/sources", json=s)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    print(f"  [OK]  #{data['id']:3d}  {s['name']}")
                    created += 1
                elif resp.status_code == 422:
                    body = resp.json()
                    print(f"  [ERR] {s['name']}: validation error — {body.get('detail', resp.text)}", file=sys.stderr)
                else:
                    print(f"  [ERR] {s['name']}: HTTP {resp.status_code} — {resp.text}", file=sys.stderr)
            except httpx.ConnectError:
                print(f"ERROR: Cannot connect to {api_url}. Is the backend running?", file=sys.stderr)
                return created
            except Exception as exc:
                print(f"  [ERR] {s['name']}: {exc}", file=sys.stderr)

    return created


async def main():
    parser = argparse.ArgumentParser(description="Import batch-1 scanners into mapping-db")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the FastAPI backend (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_LIST_PATH,
        help="Path to MASTER_LIST.md",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"ERROR: MASTER_LIST.md not found at {args.file}", file=sys.stderr)
        sys.exit(1)

    scanners = parse_master_list(args.file)
    if not scanners:
        print("No scanner entries found in batch-1 section.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(scanners)} scanner entries. Importing to {args.api_url}...")
    created = await import_scanners(args.api_url, scanners)
    print(f"\nDone. Created {created}/{len(scanners)} sources.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
