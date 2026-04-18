#!/usr/bin/env python3
"""Pick the next batch of unscanned leads and split into worker chunks.

Usage:
    python3 ops/prepare_batch.py \
        --leads /data/leads/full_20k.csv \
        --scans /data/scans \
        --batch-size 1000 \
        --workers 20 \
        --output-dir /tmp/argus_chunks

Outputs:
    /tmp/argus_chunks/chunk_00.csv ... chunk_19.csv
    Each chunk has ~50 leads with a 'domain' column (scanner-compatible).

Exit codes:
    0 = batch written, ready to scan
    1 = error
    2 = all leads already scanned, nothing to do
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from pathlib import Path


def get_scanned_domains(scans_dir: Path) -> set[str]:
    """Return set of domains that already have a scan JSON."""
    scanned = set()
    if scans_dir.exists():
        for f in scans_dir.iterdir():
            if f.suffix == ".json" and not f.name.startswith("_"):
                scanned.add(f.stem.lower())
    return scanned


def normalize_domain(value: str) -> str:
    """Strip protocol, www, trailing slash from domain-like values."""
    v = value.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.rstrip("/")


def read_leads(path: Path) -> list[dict]:
    """Read Apollo CSV and normalize column names for the scanner."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for raw in reader:
            # Build a normalized row with 'domain' column for the scanner
            row = dict(raw)

            # Ensure 'domain' column exists (scanner reads lead["domain"])
            if "domain" not in row or not row["domain"]:
                # Try company_domain, Website, etc.
                for alt in ("company_domain", "Company Domain", "website", "Website"):
                    if alt in row and row[alt]:
                        row["domain"] = normalize_domain(row[alt])
                        break

            # Ensure company_name exists
            if "company_name" not in row or not row["company_name"]:
                for alt in ("Company Name", "company", "Company", "account"):
                    if alt in row and row[alt]:
                        row["company_name"] = row[alt]
                        break

            # Skip rows without a domain
            if not row.get("domain"):
                continue

            row["domain"] = normalize_domain(row["domain"])
            rows.append(row)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare ARGUS scan batch")
    parser.add_argument("--leads", required=True, help="Master Apollo CSV")
    parser.add_argument("--scans", required=True, help="Directory with existing scan JSONs")
    parser.add_argument("--batch-size", type=int, default=1000, help="Leads per nightly batch")
    parser.add_argument("--workers", type=int, default=20, help="Number of parallel workers")
    parser.add_argument("--output-dir", required=True, help="Directory for chunk CSVs")
    args = parser.parse_args()

    leads_path = Path(args.leads)
    scans_dir = Path(args.scans)
    output_dir = Path(args.output_dir)

    if not leads_path.exists():
        print(f"ERROR: Leads file not found: {leads_path}", file=sys.stderr)
        return 1

    # Load all leads
    all_leads = read_leads(leads_path)
    print(f"Total leads in CSV: {len(all_leads)}")

    # Filter out already-scanned domains
    scanned = get_scanned_domains(scans_dir)
    print(f"Already scanned: {len(scanned)}")

    unscanned = [r for r in all_leads if r["domain"] not in scanned]
    print(f"Remaining unscanned: {len(unscanned)}")

    if not unscanned:
        print("ALL LEADS SCANNED. Nothing to do.")
        return 2

    # Pick this batch
    batch = unscanned[:args.batch_size]
    print(f"This batch: {len(batch)} leads")

    # Deduplicate by domain (Apollo can have multiple contacts per company)
    # For scanning, we only need one row per domain
    seen_domains = set()
    scan_batch = []
    for row in batch:
        d = row["domain"]
        if d not in seen_domains:
            seen_domains.add(d)
            scan_batch.append(row)

    print(f"Unique domains to scan: {len(scan_batch)}")

    # ── Write batch_leads.csv (ALL leads for tonight, including multi-contact) ──
    # This is used by `argus export` to produce the Instantly CSV.
    # Unlike the scan chunks, this is NOT deduplicated by domain — Apollo
    # may have multiple contacts per company (GF + IT-Leiter + CFO), and
    # each contact should get their own row in the Instantly upload.
    output_dir.mkdir(parents=True, exist_ok=True)

    batch_leads_path = output_dir / "batch_leads.csv"
    batch_fieldnames = list(batch[0].keys()) if batch else []
    with open(batch_leads_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=batch_fieldnames)
        writer.writeheader()
        writer.writerows(batch)
    print(f"Batch leads: {batch_leads_path} ({len(batch)} rows)")

    # ── Split scan-deduplicated batch into worker chunks ──────────────────
    chunk_size = max(1, math.ceil(len(scan_batch) / args.workers))

    # Clean old chunks
    for f in output_dir.glob("chunk_*.csv"):
        f.unlink()

    chunks_written = 0
    fieldnames = list(scan_batch[0].keys()) if scan_batch else []

    for i in range(0, len(scan_batch), chunk_size):
        chunk = scan_batch[i:i + chunk_size]
        chunk_path = output_dir / f"chunk_{chunks_written:02d}.csv"

        with open(chunk_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(chunk)

        chunks_written += 1

    print(f"Scan chunks: {chunks_written} files (~{chunk_size} domains each)")
    remaining = len(unscanned) - len(batch)
    print(f"Remaining after this batch: {remaining}")
    if remaining > 0:
        nights_left = math.ceil(remaining / args.batch_size)
        print(f"Estimated nights remaining: {nights_left}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
