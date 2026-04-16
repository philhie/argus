"""Tests for argus.export.filter — the most conversion-critical stage.

A false positive here puts an unrelated GitHub repo in a founder's inbox.
A false negative here silently drops a real company secret.
"""

from __future__ import annotations

import pytest

from argus.export.filter import (
    GITHUB_NOISE_OWNERS,
    filter_findings,
    is_company_owned_github,
    normalize_company,
)


# ──────────────────────────────────────────────────────────────────────
# Company normalization
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("dotSource SE", "dotsource"),
        ("Laseroptik GmbH", "laseroptik"),
        ("Carlsquare GmbH & Co. KG", "carlsquare"),
        ("checksum.com", "checksumcom"),
        ("Microstep AG", "microstep"),
        ("interlake.net", "interlakenet"),
        ("myConvento Ltd.", "myconvento"),
        ("Acme Inc", "acme"),
        ("Acme Inc.", "acme"),
        ("Foo LLC", "foo"),
        ("", ""),
        (None, ""),
        ("   ", ""),
    ],
)
def test_normalize_company(raw, expected):
    assert normalize_company(raw or "") == expected


# ──────────────────────────────────────────────────────────────────────
# GitHub filter — negative cases (must drop)
# ──────────────────────────────────────────────────────────────────────

def _gh(evidence: str) -> dict:
    return {
        "id": "GH-001",
        "module": "github_secrets",
        "category": "credential_exposure",
        "severity": "HOCH",
        "title": "Passwort in Repo",
        "evidence": evidence,
    }


def test_filter_drops_cirosantilli_domain_list():
    # Classic noise: expired domain list
    ev = "https://github.com/cirosantilli/expired-domain-names/blob/main/list.txt"
    assert not is_company_owned_github(_gh(ev), "laseroptik")


def test_filter_drops_apache_config_example():
    ev = "https://github.com/apache/httpd/blob/trunk/docs/config/domain.com.example"
    assert not is_company_owned_github(_gh(ev), "laseroptik")


def test_filter_drops_vala_lang_checksum_match():
    ev = "https://github.com/vala-lang/vala/blob/main/checksum.com.txt"
    assert not is_company_owned_github(_gh(ev), "checksum")


def test_filter_drops_pihole_blocklist():
    ev = "https://github.com/someuser/pihole-blocklists/blob/main/ads.txt"
    assert not is_company_owned_github(_gh(ev), "laseroptik")


def test_filter_drops_when_company_name_too_short():
    # Two-char company names are too ambiguous — must fail closed.
    ev = "https://github.com/ag/whatever/blob/main/file.txt"
    assert not is_company_owned_github(_gh(ev), "ag")


def test_filter_drops_when_company_name_empty():
    # Empty company_norm must not pass any GitHub finding.
    ev = "https://github.com/any/repo/blob/main/file.txt"
    assert not is_company_owned_github(_gh(ev), "")


# ──────────────────────────────────────────────────────────────────────
# GitHub filter — positive cases (must keep)
# ──────────────────────────────────────────────────────────────────────

def test_filter_keeps_company_name_as_path_component():
    # The Dotsource Magento plugin — real finding.
    ev = "GitHub Code Search: q=dotsource → AtelierIT/Stage_BNP/app/code/community/Dotsource/Paymentoperator/Config.php — https://github.com/AtelierIT/Stage_BNP/blob/main/app/code/community/Dotsource/Paymentoperator/Config.php"
    assert is_company_owned_github(_gh(ev), "dotsource")


def test_filter_keeps_company_owner():
    ev = "https://github.com/dotsource-de/internal/blob/main/.env"
    assert is_company_owned_github(_gh(ev), "dotsource")


# ──────────────────────────────────────────────────────────────────────
# filter_findings — full finding-level filter
# ──────────────────────────────────────────────────────────────────────

def _f(**kw) -> dict:
    base = {
        "id": "TEST-001",
        "module": "test",
        "category": "infrastructure",
        "severity": "HOCH",
        "title": "Test",
        "evidence": "",
    }
    base.update(kw)
    return base


def test_drops_info_severity():
    findings = [_f(severity="INFO"), _f(severity="HOCH")]
    kept = filter_findings(findings, "Acme GmbH")
    assert len(kept) == 1
    assert kept[0]["severity"] == "HOCH"


def test_drops_cosmetic_caa_bimi_ipcloud():
    findings = [
        _f(id="CAA-001"),
        _f(id="DNS-009"),
        _f(id="HDR-LEAK-001"),
        _f(id="IP-001-aws"),
        _f(id="IP-003-127"),
        _f(id="CLOUD-002"),
        _f(id="SHO-002"),  # must survive
    ]
    kept = filter_findings(findings, "Acme GmbH")
    kept_ids = {f["id"] for f in kept}
    assert kept_ids == {"SHO-002"}


def test_drops_github_noise_keeps_real():
    findings = [
        _f(module="github_secrets",
           evidence="https://github.com/cirosantilli/expired-domain-names/..."),
        _f(module="github_secrets",
           id="GH-002",
           evidence="https://github.com/dotsource-de/internal/...",),
    ]
    kept = filter_findings(findings, "dotSource SE")
    assert len(kept) == 1
    assert kept[0]["id"] == "GH-002"


def test_blocklist_contains_known_offenders():
    # Canary — ensure the blocklist wasn't accidentally trimmed.
    must_have = {
        "cirosantilli", "apache", "vala-lang", "MajkiIT", "r3dxpl0it",
        "wix-incubator", "fhnw-cs", "antelope-app",
    }
    assert must_have.issubset(GITHUB_NOISE_OWNERS)
