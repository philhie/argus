"""Tests for argus.export.preprocess — CVE aggregation + subdomain dedup."""

from __future__ import annotations

from argus.export.preprocess import (
    aggregate_cve_findings,
    dedup_subdomain_findings,
    preprocess,
)


def _cve(ip: str, cve: str) -> dict:
    return {
        "id": "SHO-002",
        "module": "shodan_lookup",
        "category": "infrastructure",
        "severity": "HOCH",
        "title": f"{cve} aktiv",
        "evidence": f"IP {ip}: {cve}",
        "cve_ids": [cve],
    }


def _sub(fid: str, title: str) -> dict:
    return {
        "id": fid,
        "module": "subdomain_discovery",
        "category": "infrastructure",
        "severity": "MITTEL",
        "title": title,
        "evidence": "",
    }


# ──────────────────────────────────────────────────────────────────────
# CVE aggregation
# ──────────────────────────────────────────────────────────────────────

def test_cve_aggregation_single_finding_passes_through():
    findings = [_cve("1.1.1.1", "CVE-2024-1")]
    out = aggregate_cve_findings(findings)
    assert out == findings


def test_cve_aggregation_merges_same_ip():
    findings = [
        _cve("1.1.1.1", "CVE-2024-1"),
        _cve("1.1.1.1", "CVE-2024-2"),
        _cve("1.1.1.1", "CVE-2024-3"),
    ]
    out = aggregate_cve_findings(findings)
    assert len(out) == 1
    agg = out[0]
    assert agg["id"] == "SHO-002-AGG"
    assert agg["title"] == "3 ungepatchte CVEs auf 1.1.1.1"
    assert agg["cve_ids"] == ["CVE-2024-1", "CVE-2024-2", "CVE-2024-3"]


def test_cve_aggregation_keeps_different_ips_separate():
    findings = [
        _cve("1.1.1.1", "CVE-A"),
        _cve("1.1.1.1", "CVE-B"),
        _cve("2.2.2.2", "CVE-C"),
        _cve("2.2.2.2", "CVE-D"),
    ]
    out = aggregate_cve_findings(findings)
    assert len(out) == 2
    titles = {f["title"] for f in out}
    assert "2 ungepatchte CVEs auf 1.1.1.1" in titles
    assert "2 ungepatchte CVEs auf 2.2.2.2" in titles


def test_cve_aggregation_preserves_non_cve_findings():
    other = {"id": "EX-003", "module": "exchange", "title": "/ecp"}
    findings = [
        _cve("1.1.1.1", "CVE-A"),
        _cve("1.1.1.1", "CVE-B"),
        other,
    ]
    out = aggregate_cve_findings(findings)
    assert other in out


# ──────────────────────────────────────────────────────────────────────
# Subdomain dedup
# ──────────────────────────────────────────────────────────────────────

def test_sub_002_multiple_dedup():
    findings = [
        _sub("SUB-002", "admin.acme.com erreichbar"),
        _sub("SUB-002", "administrator.acme.com erreichbar"),
        _sub("SUB-002", "panel.acme.com erreichbar"),
    ]
    out = dedup_subdomain_findings(findings)
    assert len(out) == 1
    assert out[0]["id"] == "SUB-002"
    assert out[0]["title"] == "3 Admin-Panel-Subdomains öffentlich erreichbar"


def test_sub_001_and_004_deduped_independently():
    findings = [
        _sub("SUB-001", "staging.x erreichbar"),
        _sub("SUB-001", "dev.x erreichbar"),
        _sub("SUB-004", "db.x erreichbar"),
        _sub("SUB-004", "mysql.x erreichbar"),
        _sub("SUB-004", "mongo.x erreichbar"),
    ]
    out = dedup_subdomain_findings(findings)
    by_id = {f["id"]: f for f in out}
    assert by_id["SUB-001"]["title"] == "2 Staging-Subdomains öffentlich erreichbar"
    assert by_id["SUB-004"]["title"] == "3 Datenbank-Subdomains öffentlich erreichbar"


def test_sub_single_finding_unchanged():
    findings = [_sub("SUB-002", "admin.x erreichbar")]
    out = dedup_subdomain_findings(findings)
    assert out == findings


def test_preprocess_applies_both_passes():
    findings = [
        _cve("1.1.1.1", "CVE-A"),
        _cve("1.1.1.1", "CVE-B"),
        _sub("SUB-004", "db.x erreichbar"),
        _sub("SUB-004", "mysql.x erreichbar"),
    ]
    out = preprocess(findings)
    ids = {f["id"] for f in out}
    assert "SHO-002-AGG" in ids
    assert "SUB-004" in ids
    assert len(out) == 2
