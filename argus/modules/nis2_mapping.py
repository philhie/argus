"""M18: NIS2 §30 Compliance Mapping.

Maps all findings to NIS2 §30 requirements with traffic-light scoring.
Phase 6, Step 10. No API key required — context enrichment only.

Usage: python -m argus.modules.nis2_mapping example.com
"""

from __future__ import annotations

import logging

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.nis2_mapping")

# ---------------------------------------------------------------------------
# NIS2 §30 paragraph mapping — which finding ID prefixes map to which paragraph
# ---------------------------------------------------------------------------

NIS2_PARAGRAPHS: dict[str, dict[str, object]] = {
    "§30 Abs. 2 Nr. 1": {
        "title": "Risikoanalyse und Sicherheitskonzepte",
        "prefixes": ["SHO-", "SUB-", "TAKEOVER-", "CLOUD-", "FAV-"],
    },
    "§30 Abs. 2 Nr. 2": {
        "title": "Bewältigung von Sicherheitsvorfällen",
        "prefixes": ["EX-", "CRED-"],
    },
    "§30 Abs. 2 Nr. 3": {
        "title": "Aufrechterhaltung des Betriebs",
        "prefixes": ["CERT-", "DNS-"],
    },
    "§30 Abs. 2 Nr. 4": {
        "title": "Sicherheit der Lieferkette",
        "prefixes": ["MSP-", "SC-"],
    },
    "§30 Abs. 2 Nr. 5": {
        "title": "Sicherheitsmaßnahmen bei Erwerb, Entwicklung und Wartung",
        "prefixes": ["TECH-", "GQL-", "WB-", "GORK-", "GH-"],
    },
    "§30 Abs. 2 Nr. 6": {
        "title": "Bewertung der Wirksamkeit von Risikomanagementmaßnahmen",
        "prefixes": [],  # meta — assessed by overall score
    },
    "§30 Abs. 2 Nr. 7": {
        "title": "Cyberhygiene und Schulungen",
        "prefixes": ["CRED-", "FILE-"],
    },
    "§30 Abs. 2 Nr. 8": {
        "title": "Kryptografie und Verschlüsselung",
        "prefixes": ["CERT-", "HSTS-", "HDR-"],
    },
    "§30 Abs. 2 Nr. 9": {
        "title": "Zugangskontrollen und Asset Management",
        "prefixes": ["CORS-", "EX-"],
    },
    "§30 Abs. 2 Nr. 10": {
        "title": "Multi-Faktor-Authentifizierung und sichere Kommunikation",
        "prefixes": ["EX-", "SHO-"],
    },
}

# Traffic-light colors
RED = "RED"
YELLOW = "YELLOW"
GREEN = "GREEN"
GRAY = "GRAY"


def _findings_for_paragraph(
    paragraph: str, prefixes: list[str], findings: list[Finding]
) -> list[Finding]:
    """Collect findings matching a paragraph — by annotation first, prefix as fallback."""
    # Primary: use per-finding nis2_paragraphs annotations (authoritative)
    annotated = [f for f in findings if paragraph in f.nis2_paragraphs]
    if annotated:
        return annotated
    # Fallback: prefix-based matching for findings without annotations
    if not prefixes:
        return []
    return [f for f in findings if any(f.id.startswith(p) for p in prefixes)]


def _traffic_light(matched: list[Finding]) -> str:
    """Determine the traffic-light color for a set of findings.

    - RED:    any CRITICAL finding
    - YELLOW: any HIGH or MEDIUM finding
    - GREEN:  only LOW/INFO findings or no findings at all
    """
    severities = {f.severity for f in matched}
    if Severity.CRITICAL in severities:
        return RED
    if severities & {Severity.HIGH, Severity.MEDIUM}:
        return YELLOW
    return GREEN


def map_nis2_compliance(findings: list[Finding]) -> dict[str, str]:
    """Map findings to NIS2 §30 paragraphs and return traffic-light dict."""
    compliance: dict[str, str] = {}

    for paragraph, info in NIS2_PARAGRAPHS.items():
        prefixes: list[str] = info["prefixes"]  # type: ignore[assignment]
        if not prefixes:
            # No prefixes defined — can't assess automatically
            compliance[paragraph] = GRAY
            continue
        matched = _findings_for_paragraph(paragraph, prefixes, findings)
        compliance[paragraph] = _traffic_light(matched)

    return compliance


@register
class Nis2MappingModule(BaseModule):
    name = "nis2_mapping"
    description = "NIS2 Compliance Mapping"
    phase = 6
    step = 10

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        logger.info("Mapping %d findings to NIS2 §30 paragraphs", len(context.findings))
        context.nis2_compliance = map_nis2_compliance(context.findings)

        for paragraph, color in context.nis2_compliance.items():
            title = NIS2_PARAGRAPHS[paragraph]["title"]
            logger.info("  %s (%s): %s", paragraph, title, color)

        return []  # context enrichment only — no new findings


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.nis2_mapping <domain>")
        print("  (runs NIS2 mapping against findings already in context)")
        sys.exit(1)

    # Stand-alone demo with synthetic findings
    domain = sys.argv[1]
    demo_findings = [
        Finding(
            id="DNS-001",
            module="dns_intel",
            category="infrastructure",
            title="Fehlende DNSSEC-Konfiguration",
            severity=Severity.MEDIUM,
            evidence="DNSSEC nicht aktiviert",
        ),
        Finding(
            id="CERT-001",
            module="cert_san",
            category="infrastructure",
            title="Zertifikat läuft bald ab",
            severity=Severity.HIGH,
            evidence="Ablauf in 7 Tagen",
        ),
        Finding(
            id="CRED-001",
            module="credential_exposure",
            category="credential_exposure",
            title="Zugangsdaten in Datenleck gefunden",
            severity=Severity.CRITICAL,
            evidence="3 Einträge in bekannten Leaks",
        ),
    ]

    print(f"NIS2 §30 Compliance Mapping for {domain}")
    print(f"Using {len(demo_findings)} demo findings\n")

    compliance = map_nis2_compliance(demo_findings)
    for paragraph, color in compliance.items():
        title = NIS2_PARAGRAPHS[paragraph]["title"]
        print(f"  {color:6s}  {paragraph} — {title}")
