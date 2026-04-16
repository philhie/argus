"""Integration test for the full export pipeline.

Runs against real scan JSONs dropped into tests/fixtures/scans/. Skipped
cleanly when the directory is empty, so CI doesn't break before fixtures
land. Validates every output invariant that matters for email quality:

  1. No [REVIEW] tags in any cell
  2. No unresolved {placeholder} syntax in any body field
  3. finding_1_short <= 50 chars
  4. No GitHub noise owner name appears in any cell
  5. tier is always one of {A, B, C}
  6. downtime_cost formatted correctly when employee_count set
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

from argus.export.filter import GITHUB_NOISE_OWNERS
from argus.export.pipeline import run_export_pipeline
from argus.export.translator import MAX_SHORT_LENGTH, REVIEW_TAG

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SCANS_DIR = FIXTURE_DIR / "scans"
LEADS_CSV = FIXTURE_DIR / "apollo_sample.csv"


def _has_fixtures() -> bool:
    return SCANS_DIR.exists() and any(SCANS_DIR.glob("*.json"))


skip_if_no_fixtures = pytest.mark.skipif(
    not _has_fixtures(),
    reason=(
        "Drop scan JSONs into tests/fixtures/scans/ to run integration tests. "
        "Expected 11 domains per spec §16.3."
    ),
)


_PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")


@pytest.fixture(scope="module")
def export_output(tmp_path_factory) -> list[dict]:
    """Run the real pipeline once, parse the CSV into a list of dicts."""
    out_path = tmp_path_factory.mktemp("export") / "instantly.csv"
    run_export_pipeline(
        leads_path=LEADS_CSV,
        scans_dir=SCANS_DIR,
        output_path=out_path,
        use_llm=False,
        strict=True,
    )
    with open(out_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ──────────────────────────────────────────────────────────────────────
# Output-quality invariants
# ──────────────────────────────────────────────────────────────────────

@skip_if_no_fixtures
def test_pipeline_produces_rows(export_output):
    assert export_output, "pipeline produced zero rows"


@skip_if_no_fixtures
def test_no_review_tag_anywhere(export_output):
    offenders = [
        (row["company_domain"], col, val)
        for row in export_output
        for col, val in row.items()
        if REVIEW_TAG in str(val)
    ]
    assert not offenders, f"[REVIEW] leaked into output: {offenders}"


@skip_if_no_fixtures
def test_no_unresolved_placeholders(export_output):
    body_fields = ["finding_1_short", "finding_1_what", "finding_2_what", "finding_3_what"]
    offenders = [
        (row["company_domain"], field, row[field])
        for row in export_output
        for field in body_fields
        if _PLACEHOLDER_RE.search(row[field] or "")
    ]
    assert not offenders, f"unresolved placeholders in output: {offenders}"


@skip_if_no_fixtures
def test_finding_1_short_under_limit(export_output):
    too_long = [
        (row["company_domain"], row["finding_1_short"])
        for row in export_output
        if len(row["finding_1_short"]) > MAX_SHORT_LENGTH
    ]
    assert not too_long, f"finding_1_short exceeds {MAX_SHORT_LENGTH} chars: {too_long}"


@skip_if_no_fixtures
def test_tier_is_valid(export_output):
    for row in export_output:
        assert row["tier"] in ("A", "B", "C"), f"invalid tier: {row['tier']}"


@skip_if_no_fixtures
def test_no_github_noise_owner_in_output(export_output):
    for row in export_output:
        blob = " ".join(str(v) for v in row.values())
        for owner in GITHUB_NOISE_OWNERS:
            assert owner not in blob, (
                f"noise owner {owner!r} leaked into row for {row['company_domain']}"
            )


@skip_if_no_fixtures
def test_downtime_cost_format(export_output):
    pattern = re.compile(r"^rund \d{1,3}(?:\.\d{3})*€$")
    for row in export_output:
        if row["employee_count"] and row["employee_count"].isdigit():
            assert pattern.match(row["downtime_cost"]), (
                f"bad downtime_cost for {row['company_domain']}: {row['downtime_cost']!r}"
            )


# ──────────────────────────────────────────────────────────────────────
# Spec §16.3 validation matrix (per-domain assertions)
# ──────────────────────────────────────────────────────────────────────

_EXPECTED = {
    "laseroptik.com":  {"tier": "A", "short_contains": "Datenbank"},
    "carlsquare.com":  {"tier": "A", "short_contains": "Datenbank"},
    "microstep.com":   {"tier": "A", "short_contains": "phpMyAdmin"},
    "cfc-contor.com":  {"tier": "A", "short_contains": "Konfigurationsdatei"},
    "dotsource.de":    {"tier": "A", "short_contains": "Passwort"},
    "checksum.com":    {"tier": "A", "short_contains": "Exchange"},
    "interlake.net":   {"tier": "A", "short_contains": "Mail"},
    "tpa-global.com":  {"tier": "B", "short_contains": "PDF"},
    "gracher.de":      {"tier": "B", "short_contains": "TLS"},
    "myconvento.com":  {"tier": "B", "short_contains": "DMARC"},
    "oli-move.de":     {"tier": "B", "short_contains": "DMARC"},
}


@skip_if_no_fixtures
def test_expected_tier_and_finding_per_domain(export_output):
    by_domain = {row["company_domain"]: row for row in export_output}
    for domain, spec in _EXPECTED.items():
        if domain not in by_domain:
            continue  # partial-fixtures run: don't hard-fail on missing
        row = by_domain[domain]
        assert row["tier"] == spec["tier"], (
            f"{domain}: expected tier {spec['tier']}, got {row['tier']}"
        )
        assert spec["short_contains"] in row["finding_1_short"], (
            f"{domain}: finding_1_short {row['finding_1_short']!r} "
            f"does not contain {spec['short_contains']!r}"
        )


# ──────────────────────────────────────────────────────────────────────
# Skippable-path smoke test (always runs)
# ──────────────────────────────────────────────────────────────────────

def test_pipeline_runs_with_empty_scans_directory(tmp_path):
    """Pipeline must handle 'no scans at all' gracefully — all leads land
    in the missing bucket, no exceptions."""
    empty_scans = tmp_path / "empty_scans"
    empty_scans.mkdir()
    out = tmp_path / "out.csv"

    stats = run_export_pipeline(
        leads_path=LEADS_CSV,
        scans_dir=empty_scans,
        output_path=out,
        use_llm=False,
        strict=True,
    )
    assert stats["written"] == 0
    assert stats["missing"] == 11  # sample CSV has 11 rows
    # Output file exists and contains just the header.
    with open(out, encoding="utf-8") as f:
        assert f.readline().strip().startswith('"email"')


def test_pipeline_handles_synthetic_scan(tmp_path):
    """Smoke test against a synthetic scan JSON so we validate the
    render-path without requiring the full fixture set."""
    scans = tmp_path / "scans"
    scans.mkdir()
    synth = {
        "domain": "laseroptik.com",
        "company_name": "Laseroptik GmbH",
        "findings_total": 5,
        "findings_critical": 1,
        "findings": [
            {
                "id": "SHO-001",
                "module": "shodan_lookup",
                "category": "infrastructure",
                "severity": "KRITISCH",
                "title": "MySQL offen auf Port 3306",
                "evidence": "IP 5.6.7.8, Port 3306, mail.laseroptik.com",
                "cve_ids": [],
            },
            {
                "id": "DNS-006",
                "module": "dns_intel",
                "category": "email_security",
                "severity": "KRITISCH",
                "title": "Kein DMARC",
                "evidence": "",
                "cve_ids": [],
            },
            {
                "id": "TLS-001",
                "module": "tls_analysis",
                "category": "infrastructure",
                "severity": "HOCH",
                "title": "TLS 1.0 aktiv",
                "evidence": "",
                "cve_ids": [],
            },
        ],
    }
    (scans / "laseroptik.com.json").write_text(json.dumps(synth), encoding="utf-8")

    leads_path = tmp_path / "leads.csv"
    leads_path.write_text(
        "email,first_name,last_name,company_domain,employee_count\n"
        "info@laseroptik.com,Max,Muster,laseroptik.com,150\n",
        encoding="utf-8",
    )

    out = tmp_path / "out.csv"
    stats = run_export_pipeline(
        leads_path=leads_path,
        scans_dir=scans,
        output_path=out,
        use_llm=False,
        strict=True,
    )

    assert stats["written"] == 1
    assert stats["tier_a"] == 1

    with open(out, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    row = rows[0]
    assert row["tier"] == "A"
    assert "Datenbank" in row["finding_1_short"]
    assert row["specific_subdomain"] == "mail.laseroptik.com"
    assert row["downtime_cost"] == "rund 36.000€"
    assert REVIEW_TAG not in row["finding_1_what"]
    assert not _PLACEHOLDER_RE.search(row["finding_1_what"])
