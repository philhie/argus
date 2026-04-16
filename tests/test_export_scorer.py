"""Tests for argus.export.scorer.

Table-driven against the spec §8.5 matrix — every row must match exactly,
otherwise the tier thresholds in §9.3 don't land correctly.
"""

from __future__ import annotations

import pytest

from argus.export.scorer import score_finding, score_findings


def _f(**kw) -> dict:
    base = {
        "id": "X-000",
        "module": "",
        "category": "",
        "severity": "INFO",
        "title": "",
        "evidence": "",
    }
    base.update(kw)
    return base


# ──────────────────────────────────────────────────────────────────────
# Spec §8.5 matrix — every value must match exactly.
# ──────────────────────────────────────────────────────────────────────

def test_mysql_open_scores_23():
    # KRITISCH(10) + infra(4) + shodan verifiable(5) + critical_boost(4) = 23
    f = _f(id="SHO-001", module="shodan_lookup", category="infrastructure",
           severity="KRITISCH", title="MySQL offen auf Port 3306")
    assert score_finding(f) == 23


def test_exchange_ecp_scores_32():
    # KRITISCH(10) + exchange(8) + exchange_verifiable(5) + crit(4) + ecp(5)
    f = _f(id="EX-003", module="exchange", category="exchange_exposure",
           severity="KRITISCH", title="/ecp öffentlich")
    assert score_finding(f) == 32


def test_webconfig_scores_18():
    # HOCH(7) + webapp(2) + file_exp_verifiable(5) + file_boost(4) = 18
    f = _f(id="FILE-WEBCONFIG", module="file_exposure", category="web_application",
           severity="HOCH", title="/web.config öffentlich")
    assert score_finding(f) == 18


def test_hibp_password_scores_24():
    # KRITISCH(10) + cred(6) + crit(4) + hibp(4) = 24
    f = _f(id="CRED-001", module="credential_exposure",
           category="credential_exposure", severity="KRITISCH",
           title="info@acme.de in Leck mit Passwort")
    assert score_finding(f) == 24


def test_phpmyadmin_scores_14():
    # HOCH(7) + webapp(2) + admin_verifiable(5) = 14
    f = _f(id="ADM-001", module="admin_panel", category="web_application",
           severity="HOCH", title="phpMyAdmin offen")
    assert score_finding(f) == 14


def test_dmarc_none_policy_scores_10():
    # HOCH(7) + email(3) = 10
    f = _f(id="DNS-004", module="dns_intel", category="email_security",
           severity="HOCH", title="DMARC p=none")
    assert score_finding(f) == 10


def test_tls10_scores_11():
    # HOCH(7) + infra(4) = 11
    f = _f(id="TLS-001", module="tls_analysis", category="infrastructure",
           severity="HOCH", title="TLS 1.0 aktiv")
    assert score_finding(f) == 11


def test_no_dmarc_scores_17():
    # KRITISCH(10) + email(3) + crit(4) = 17
    f = _f(id="DNS-006", module="dns_intel", category="email_security",
           severity="KRITISCH", title="Kein DMARC")
    assert score_finding(f) == 17


def test_spf_weak_scores_10():
    # HOCH(7) + email(3) = 10
    f = _f(id="DNS-001", module="dns_intel", category="email_security",
           severity="HOCH", title="SPF ~all")
    assert score_finding(f) == 10


def test_no_dkim_scores_10():
    # HOCH(7) + email(3) = 10
    f = _f(id="DNS-003", module="dns_intel", category="email_security",
           severity="HOCH", title="Kein DKIM")
    assert score_finding(f) == 10


# ──────────────────────────────────────────────────────────────────────
# Edge cases
# ──────────────────────────────────────────────────────────────────────

def test_info_severity_scores_zero():
    assert score_finding(_f(severity="INFO")) == 0


def test_score_findings_returns_sorted_desc():
    findings = [
        _f(id="LOW",  module="dns_intel", category="email_security", severity="MITTEL",   title="x"),
        _f(id="HIGH", module="shodan_lookup", category="infrastructure", severity="KRITISCH", title="MySQL"),
        _f(id="MID",  module="tls_analysis", category="infrastructure", severity="HOCH", title="TLS 1.0"),
    ]
    scored = score_findings(findings)
    assert [s["finding"]["id"] for s in scored] == ["HIGH", "MID", "LOW"]
    assert scored[0]["score"] > scored[1]["score"] > scored[2]["score"]


def test_exchange_ecp_and_powershell_both_get_bonus():
    f = _f(id="EX-004", module="exchange", category="exchange_exposure",
           severity="KRITISCH", title="/PowerShell offen")
    assert score_finding(f) == 32


def test_cred_004_gf_email_gets_hibp_boost():
    # GF-specific breach is the highest-converting finding — must score
    # at least as well as CRED-001 (plaintext password breach).
    # KRITISCH(10) + cred(6) + crit(4) + hibp(4) = 24
    f = _f(id="CRED-004", module="credential_exposure",
           category="credential_exposure", severity="KRITISCH",
           title="GF-Mail in Leck")
    assert score_finding(f) == 24
