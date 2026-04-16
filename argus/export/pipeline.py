"""Top-level export pipeline.

Flow per lead:
    1. Load scan JSON
    2. Pre-process (CVE aggregation, subdomain dedup)
    3. Filter (INFO, cosmetic, GitHub noise)
    4. Score → sort desc
    5. Tier classification (+ maybe_upgrade)
    6. Top-3 selection (category-diverse)
    7. Translate each top-3 finding via template
    8. Merge lead + scan + translations into one Instantly row
"""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path

from argus.export.filter import filter_findings
from argus.export.leadcsv import calc_downtime, pick_subdomain, read_leads
from argus.export.preprocess import preprocess
from argus.export.scorer import score_findings
from argus.export.selector import select_top_3
from argus.export.tier import classify_tier, maybe_upgrade
from argus.export.translator import (
    MAX_SHORT_LENGTH,
    REVIEW_TAG,
    translate_finding,
)

logger = logging.getLogger("argus")

CSV_FIELDS = [
    "email",
    "first_name",
    "last_name",
    "title",
    "company_name",
    "company_domain",
    "linkedin_url",
    "industry",
    "company_size",
    "city",
    "tier",
    "specific_subdomain",
    "finding_1_short",
    "finding_1_what",
    "finding_2_what",
    "finding_3_what",
    "total_findings",
    "critical_count",
    "employee_count",
    "downtime_cost",
]

# Fields where a stray '{placeholder}' substring would leak into the email.
# Used by _has_unresolved_placeholder for strict-mode validation.
_BODY_FIELDS = (
    "finding_1_short",
    "finding_1_what",
    "finding_2_what",
    "finding_3_what",
)

_PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")


def _has_unresolved_placeholder(row: dict) -> bool:
    return any(_PLACEHOLDER_RE.search(row.get(f, "") or "") for f in _BODY_FIELDS)


def _has_review_tag(row: dict) -> bool:
    return any(REVIEW_TAG in (row.get(f, "") or "") for f in _BODY_FIELDS)


def _load_scans(scans_dir: Path) -> dict[str, dict]:
    """Build domain → scan-data index from a directory of JSON files."""
    index: dict[str, dict] = {}
    for path in sorted(scans_dir.glob("*.json")):
        if path.name.startswith("_"):  # skip summaries
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load %s: %s", path, exc)
            continue
        domain = (data.get("domain") or path.stem).strip().lower()
        if domain:
            index[domain] = data
    return index


def process_lead(lead: dict, scan_data: dict, use_llm: bool = False) -> dict | None:
    """Apply the full pipeline to one lead. Returns None when SKIP."""
    findings_raw = scan_data.get("findings", []) or []

    # Scanner sometimes fails to populate company_name — fall back to the
    # Apollo value so the GitHub filter still has a usable ownership signal.
    company_name_for_filter = (
        (scan_data.get("company_name") or "").strip()
        or (lead.get("company_name") or "").strip()
    )

    findings = preprocess(findings_raw)
    findings = filter_findings(findings, company_name_for_filter)
    if not findings:
        return None

    scored = score_findings(findings)

    tier = classify_tier(scored)
    tier = maybe_upgrade(tier, scored)
    if tier == "SKIP":
        return None

    top = select_top_3(scored)

    translations = [translate_finding(e["finding"], scan_data, use_llm) for e in top]
    while len(translations) < 3:
        translations.append({"short": "", "what": ""})

    employee_count = lead.get("employee_count", "")

    return {
        "email": lead.get("email", ""),
        "first_name": lead.get("first_name", ""),
        "last_name": lead.get("last_name", ""),
        "title": lead.get("title", "") or "Geschäftsführer",
        "company_name": (
            lead.get("company_name", "")
            or scan_data.get("company_name", "")
            or scan_data.get("domain", "")
        ),
        "company_domain": scan_data.get("domain", ""),
        "linkedin_url": lead.get("linkedin_url", ""),
        "industry": lead.get("industry", ""),
        "company_size": lead.get("company_size", ""),
        "city": lead.get("city", ""),
        "tier": tier,
        "specific_subdomain": pick_subdomain(scan_data),
        "finding_1_short": translations[0]["short"],
        "finding_1_what": translations[0]["what"],
        "finding_2_what": translations[1]["what"],
        "finding_3_what": translations[2]["what"],
        "total_findings": str(scan_data.get("findings_total", 0)),
        "critical_count": str(scan_data.get("findings_critical", 0)),
        "employee_count": employee_count,
        "downtime_cost": calc_downtime(employee_count),
    }


def run_export_pipeline(
    leads_path: str | Path,
    scans_dir: str | Path,
    output_path: str | Path,
    use_llm: bool = False,
    strict: bool = True,
) -> dict:
    """Run the full export and return summary stats."""
    leads_path = Path(leads_path)
    scans_dir = Path(scans_dir)
    output_path = Path(output_path)

    if use_llm:
        logger.info(
            "LLM fallback requested; templates cover 100%% of known finding "
            "types — no API calls made."
        )

    scan_index = _load_scans(scans_dir)
    logger.info("Loaded %d scan JSON(s) from %s", len(scan_index), scans_dir)

    stats = {
        "written": 0,
        "skipped": 0,
        "missing": 0,
        "no_email": 0,
        "review_skipped": 0,
        "tier_a": 0,
        "tier_b": 0,
        "tier_c": 0,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for lead in read_leads(leads_path):
            email = (lead.get("email", "") or "").strip()
            if not email or "@" not in email:
                stats["no_email"] += 1
                logger.info("[SKIP] Lead has no usable email")
                continue

            domain = (lead.get("company_domain", "") or "").strip().lower()
            if not domain or domain not in scan_index:
                stats["missing"] += 1
                logger.info("[SKIP] No scan for domain: %s", domain or "<empty>")
                continue

            scan_data = scan_index[domain]
            row = process_lead(lead, scan_data, use_llm=use_llm)
            if row is None:
                stats["skipped"] += 1
                logger.info("[SKIP] Tier=SKIP for %s (insufficient findings)", domain)
                continue

            if strict and (_has_review_tag(row) or _has_unresolved_placeholder(row)):
                stats["review_skipped"] += 1
                logger.warning(
                    "[SKIP] %s has unresolved template (review_skipped)", domain
                )
                continue

            writer.writerow(row)
            stats["written"] += 1
            stats[f"tier_{row['tier'].lower()}"] += 1

            # Runtime subject-line length guard — catches escapes from
            # template definition tests if data widens a short beyond 50.
            short = row.get("finding_1_short", "") or ""
            if len(short) > MAX_SHORT_LENGTH:
                logger.warning(
                    "finding_1_short over %d chars for %s: %r",
                    MAX_SHORT_LENGTH, domain, short,
                )

    return stats
