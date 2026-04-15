"""M28: DNSSEC Validation.

Usage: python -m argus.modules.dnssec true-fruits.com
"""

from __future__ import annotations

import logging

import dns.resolver

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.dnssec")


def check_dnssec(domain: str) -> bool:
    """Check if DNSSEC is configured by looking for DNSKEY records."""
    try:
        answers = dns.resolver.resolve(domain, 'DNSKEY')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return False
    except Exception:
        return False


@register
class DnssecModule(BaseModule):
    name = "dnssec"
    description = "DNSSEC Validation"
    phase = 1
    step = 1

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        enabled = check_dnssec(domain)
        context.dns.dnssec_enabled = enabled

        if not enabled:
            return [Finding(
                id="DNSSEC-001",
                module="dnssec",
                category="infrastructure",
                title="Kein DNSSEC konfiguriert — DNS-Spoofing möglich",
                description=(
                    "Ohne DNSSEC können DNS-Antworten gefälscht werden. "
                    "Ein Angreifer kann den DNS-Traffic manipulieren und Benutzer "
                    "auf gefälschte Websites umleiten (DNS Cache Poisoning)."
                ),
                severity=Severity.MEDIUM,
                evidence=f"dig DNSKEY {domain} → Kein DNSKEY-Record gefunden",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation="DNSSEC bei Ihrem DNS-Provider aktivieren und DS-Records beim Registrar hinterlegen.",
            )]
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.dnssec <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    enabled = check_dnssec(domain)
    print(f"DNSSEC for {domain}: {'ENABLED' if enabled else 'NOT CONFIGURED'}")
