"""Tests for core data models."""

import json

from argus.models import DNSResult, Finding, ScanContext, ScanResult, Severity


def test_finding_json_roundtrip():
    finding = Finding(
        id="DNS-001",
        module="dns_intel",
        category="email_security",
        title="SPF-Record mit schwachem Mechanismus (~all)",
        severity=Severity.HIGH,
        evidence="dig TXT example.com",
        nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
        remediation="SPF auf -all umstellen.",
    )
    data = finding.model_dump()
    assert data["severity"] == "HOCH"
    assert data["id"] == "DNS-001"

    # Roundtrip through JSON
    json_str = json.dumps(data)
    restored = json.loads(json_str)
    assert restored["title"] == finding.title


def test_scan_context_accumulates_ips():
    ctx = ScanContext(domain="example.com")
    ctx.discovered_ips.add("1.2.3.4")
    ctx.discovered_ips.add("5.6.7.8")
    ctx.discovered_ips.add("1.2.3.4")  # duplicate
    assert len(ctx.discovered_ips) == 2


def test_dns_result_defaults():
    dns = DNSResult()
    assert dns.mx_records == []
    assert dns.spf_record is None
    assert dns.dmarc_record is None
    assert dns.dkim_selectors_found == []
    assert dns.mta_sts is False
    assert dns.dane_tlsa is False
    assert dns.bimi is False
    assert dns.dnssec_enabled is False
    assert dns.caa_records == []


def test_scan_result_serialization():
    result = ScanResult(
        domain="example.com",
        company_name="Example GmbH",
        scan_timestamp="2026-04-15T12:00:00Z",
        exposure_score=42,
        findings_critical=2,
        findings_high=3,
        findings_total=10,
        top_finding_1="Finding 1",
        subject_line="Example GmbH — Finding 1",
    )
    data = result.model_dump()
    json_str = json.dumps(data, default=str)
    assert "Example GmbH" in json_str
    assert data["exposure_score"] == 42


def test_severity_values_german():
    assert Severity.CRITICAL.value == "KRITISCH"
    assert Severity.HIGH.value == "HOCH"
    assert Severity.MEDIUM.value == "MITTEL"
    assert Severity.LOW.value == "NIEDRIG"
    assert Severity.INFO.value == "INFO"
