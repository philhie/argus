"""M33: WHOIS Expiration Check.

Usage: python -m argus.modules.whois_check true-fruits.com
"""

from __future__ import annotations

import logging
from datetime import datetime

import whois

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.whois_check")


def check_whois(domain: str) -> tuple[str | None, int | None, str | None]:
    """Check domain WHOIS. Returns (expiry_date_str, days_left, registrar)."""
    try:
        w = whois.whois(domain)
        expiry = w.expiration_date
        if isinstance(expiry, list):
            expiry = expiry[0]
        if expiry is None:
            return None, None, w.registrar

        if isinstance(expiry, datetime):
            days_left = (expiry - datetime.now()).days
            return expiry.isoformat(), days_left, w.registrar

        return str(expiry), None, w.registrar
    except Exception as e:
        logger.debug(f"WHOIS lookup failed for {domain}: {e}")
        return None, None, None


@register
class WhoisCheckModule(BaseModule):
    name = "whois_check"
    description = "Domain WHOIS Expiration Check"
    phase = 1
    step = 1

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        expiry_str, days_left, registrar = check_whois(domain)

        context.dns.whois_expiry_date = expiry_str
        context.dns.whois_days_until_expiry = days_left
        context.dns.whois_registrar = registrar

        if days_left is not None and days_left < 90:
            severity = Severity.HIGH if days_left < 30 else Severity.MEDIUM
            return [Finding(
                id="WHOIS-001",
                module="whois_check",
                category="infrastructure",
                title=f"Domain läuft in {days_left} Tagen ab — Takeover-Risiko",
                description=(
                    f"Die Domain {domain} läuft am {expiry_str} ab. "
                    f"Wenn die Domain nicht rechtzeitig verlängert wird, kann sie "
                    f"von Dritten registriert und für Phishing oder "
                    f"Markenrechtsverletzungen missbraucht werden."
                ),
                severity=severity,
                evidence=f"WHOIS {domain} → Expiration: {expiry_str} ({days_left} Tage verbleibend)",
                nis2_paragraphs=["§30 Abs. 2 Nr. 3"],
                remediation="Domain-Verlängerung sofort durchführen und Auto-Renew aktivieren.",
            )]
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.whois_check <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    expiry, days, registrar = check_whois(domain)
    print(f"Domain: {domain}")
    print(f"Registrar: {registrar}")
    print(f"Expiry: {expiry}")
    print(f"Days left: {days}")
