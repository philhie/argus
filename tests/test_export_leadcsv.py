"""Tests for argus.export.leadcsv — CSV reading, downtime calc, subdomain pick."""

from __future__ import annotations

from pathlib import Path

from argus.export.leadcsv import calc_downtime, pick_subdomain, read_leads


# ──────────────────────────────────────────────────────────────────────
# Downtime calculation
# ──────────────────────────────────────────────────────────────────────

def test_downtime_cost_100_employees():
    # 100 * 30 * 8 = 24000 → rounded to 24000
    assert calc_downtime("100") == "rund 24.000€"


def test_downtime_cost_80_employees():
    # 80 * 30 * 8 = 19200 → rounded to 19000
    assert calc_downtime("80") == "rund 19.000€"


def test_downtime_cost_empty_returns_empty():
    assert calc_downtime("") == ""
    assert calc_downtime(None) == ""


def test_downtime_cost_non_numeric_returns_empty():
    assert calc_downtime("TODO") == ""
    assert calc_downtime("many") == ""


def test_downtime_cost_zero_returns_empty():
    assert calc_downtime("0") == ""


def test_downtime_cost_strips_separators():
    # Apollo sometimes emits "1,000" or "1.000"
    assert calc_downtime("1,000") == "rund 240.000€"


# ──────────────────────────────────────────────────────────────────────
# Subdomain pick
# ──────────────────────────────────────────────────────────────────────

def test_pick_subdomain_prefers_mail():
    scan = {
        "domain": "acme.com",
        "findings": [
            {"evidence": "Checked https://random.acme.com/path"},
            {"evidence": "Exchange at mail.acme.com/owa"},
        ],
    }
    # Iteration order matters — interesting-prefix wins regardless of order
    assert pick_subdomain(scan) == "mail.acme.com"


def test_pick_subdomain_falls_back_to_apex():
    scan = {"domain": "acme.com", "findings": [{"evidence": "no subdomain here"}]}
    assert pick_subdomain(scan) == "acme.com"


def test_pick_subdomain_empty_domain():
    assert pick_subdomain({"domain": "", "findings": []}) == ""


def test_pick_subdomain_checks_all_matches_in_evidence():
    # Single evidence string with two subdomains — the interesting one
    # is second in the string. First-match-only logic would miss it.
    scan = {
        "domain": "acme.com",
        "findings": [
            {"evidence": "DNS A-Record: random.acme.com → 1.1.1.1, mail.acme.com → 2.2.2.2"},
        ],
    }
    assert pick_subdomain(scan) == "mail.acme.com"


# ──────────────────────────────────────────────────────────────────────
# CSV column normalization
# ──────────────────────────────────────────────────────────────────────

def test_read_leads_canonicalizes_apollo_columns(tmp_path: Path):
    csv_path = tmp_path / "apollo.csv"
    csv_path.write_text(
        "Email,First Name,Last Name,Company Domain,Employee Count\n"
        "phil@example.com,Phil,Hiersemenzel,acme.com,50\n"
    )
    leads = list(read_leads(csv_path))
    assert len(leads) == 1
    lead = leads[0]
    assert lead["email"] == "phil@example.com"
    assert lead["first_name"] == "Phil"
    assert lead["last_name"] == "Hiersemenzel"
    assert lead["company_domain"] == "acme.com"
    assert lead["employee_count"] == "50"


def test_read_leads_case_and_punctuation_insensitive(tmp_path: Path):
    csv_path = tmp_path / "apollo.csv"
    csv_path.write_text(
        "EMAIL,first_name,LAST-NAME,company-domain\n"
        "a@b.com,Alice,Bob,example.com\n"
    )
    leads = list(read_leads(csv_path))
    assert leads[0]["email"] == "a@b.com"
    assert leads[0]["first_name"] == "Alice"
    assert leads[0]["last_name"] == "Bob"
    assert leads[0]["company_domain"] == "example.com"


def test_read_leads_fills_missing_columns_with_empty(tmp_path: Path):
    csv_path = tmp_path / "apollo.csv"
    csv_path.write_text(
        "email,company_domain\n"
        "x@y.com,acme.com\n"
    )
    lead = next(read_leads(csv_path))
    assert lead["first_name"] == ""
    assert lead["employee_count"] == ""
    assert lead["linkedin_url"] == ""
