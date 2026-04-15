"""Tests for the scoring engine."""

from argus.models import Finding, Severity
from argus.scoring import calculate_exposure_score


def _make_finding(severity: Severity, category: str = "email_security") -> Finding:
    return Finding(
        id="TEST-001",
        module="test",
        category=category,
        title="Test finding",
        severity=severity,
        evidence="test evidence",
    )


def test_empty_findings_score_zero():
    score, breakdown = calculate_exposure_score([])
    assert score == 0
    assert breakdown.email_security == 0
    assert breakdown.infrastructure == 0


def test_single_critical_finding():
    findings = [_make_finding(Severity.CRITICAL, "email_security")]
    score, breakdown = calculate_exposure_score(findings)
    assert breakdown.email_security == 25  # CRITICAL = 25 points
    assert score == 5  # 25 * 0.20 = 5


def test_single_high_finding():
    findings = [_make_finding(Severity.HIGH, "infrastructure")]
    score, breakdown = calculate_exposure_score(findings)
    assert breakdown.infrastructure == 15  # HIGH = 15 points
    assert score == 3  # 15 * 0.25 = 3.75 -> int = 3


def test_info_findings_contribute_zero():
    findings = [_make_finding(Severity.INFO, "web_application")]
    score, breakdown = calculate_exposure_score(findings)
    assert breakdown.web_application == 0
    assert score == 0


def test_category_cap_at_100():
    # 5 CRITICAL findings in one category = 125, capped at 100
    findings = [_make_finding(Severity.CRITICAL, "email_security") for _ in range(5)]
    score, breakdown = calculate_exposure_score(findings)
    assert breakdown.email_security == 100


def test_total_score_cap_at_100():
    # Max out every category
    findings = []
    for cat in ["email_security", "infrastructure", "web_application",
                "credential_exposure", "exchange_exposure", "supply_chain"]:
        for _ in range(5):
            findings.append(_make_finding(Severity.CRITICAL, cat))
    score, breakdown = calculate_exposure_score(findings)
    assert score == 100


def test_multiple_categories():
    findings = [
        _make_finding(Severity.HIGH, "email_security"),     # 15 * 0.20 = 3
        _make_finding(Severity.MEDIUM, "infrastructure"),   # 8 * 0.25 = 2
        _make_finding(Severity.LOW, "web_application"),     # 3 * 0.20 = 0.6
    ]
    score, breakdown = calculate_exposure_score(findings)
    assert breakdown.email_security == 15
    assert breakdown.infrastructure == 8
    assert breakdown.web_application == 3
    assert score == 5  # 3 + 2 + 0.6 = 5.6 -> int = 5
