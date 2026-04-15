"""CLI entry point for KENGO ARGUS scanner."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys

from argus.scanner import save_result, scan_domain


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.StreamHandler()],
    )


def cmd_scan(args: argparse.Namespace) -> None:
    """Run scan on domain(s)."""
    leads: list[dict] = []

    if args.domain:
        leads.append({
            "domain": args.domain,
            "company_name": args.company or args.domain,
        })
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            leads = list(csv.DictReader(f))
    else:
        print("Error: Provide --domain or --input", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        leads = leads[:args.limit]

    max_step = args.steps if args.steps else 10

    os.makedirs(args.output, exist_ok=True)

    print(f"KENGO ARGUS — Scanning {len(leads)} domain(s)")
    print(f"Output: {args.output}")
    print(f"Max step: {max_step}")
    print()

    summary_rows: list[dict] = []

    for lead in leads:
        domain = lead["domain"]
        company = lead.get("company_name", domain)
        output_file = os.path.join(args.output, f"{domain}.json")

        # Skip already scanned (unless --force)
        if os.path.exists(output_file) and not args.force:
            print(f"  Skipping {domain} (already scanned, use --force to rescan)")
            continue

        print(f"{'='*60}")
        print(f"Scanning: {domain} ({company})")
        print(f"{'='*60}")

        try:
            result = scan_domain(
                domain=domain,
                company_name=company,
                gf_name=lead.get("gf_name"),
                gf_email=lead.get("gf_email"),
                max_step=max_step,
            )

            filepath = save_result(result, args.output)
            print(f"  Score: {result.exposure_score}/100 | "
                  f"Findings: {result.findings_total} | "
                  f"Critical: {result.findings_critical} | "
                  f"High: {result.findings_high}")
            print(f"  Saved: {filepath}")
            print(f"  Duration: {result.scan_duration_seconds}s")

            summary_rows.append({
                "domain": domain,
                "company_name": company,
                "score": result.exposure_score,
                "findings_critical": result.findings_critical,
                "findings_high": result.findings_high,
                "findings_total": result.findings_total,
                "top_finding_1": result.top_finding_1,
                "top_finding_2": result.top_finding_2,
                "top_finding_3": result.top_finding_3,
                "personalization_block": result.personalization_block,
                "subject_line": result.subject_line,
            })

        except Exception as e:
            print(f"  ERROR scanning {domain}: {e}")
            continue

        print()

    # Write summary CSV
    if summary_rows:
        summary_file = os.path.join(args.output, "_summary.csv")
        with open(summary_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(sorted(summary_rows, key=lambda x: x["score"], reverse=True))
        print(f"Summary: {summary_file}")

    print(f"\nScan complete. {len(summary_rows)} domain(s) processed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="argus",
        description="KENGO ARGUS — Automated Passive Reconnaissance Engine",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    subparsers = parser.add_subparsers(dest="command")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan domain(s)")
    scan_parser.add_argument("--domain", "-d", help="Single domain to scan")
    scan_parser.add_argument("--company", "-c", help="Company name (with --domain)")
    scan_parser.add_argument("--input", "-i", help="CSV file with leads")
    scan_parser.add_argument("--output", "-o", default="results", help="Output directory")
    scan_parser.add_argument("--limit", "-l", type=int, help="Max domains to scan")
    scan_parser.add_argument("--steps", "-s", type=int, help="Only run modules up to this step (1-10)")
    scan_parser.add_argument("--force", "-f", action="store_true", help="Rescan already-scanned domains")
    scan_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    setup_logging(getattr(args, "verbose", False))

    if args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
