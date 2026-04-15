"""M32: CAA Records Check.

Usage: python -m argus.modules.caa true-fruits.com
"""

from __future__ import annotations

import logging

import dns.resolver

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.caa")


def check_caa(domain: str) -> list[str]:
    """Check for CAA records. Returns list of CAA record strings."""
    try:
        answers = dns.resolver.resolve(domain, 'CAA')
        return [str(r) for r in answers]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return []
    except Exception:
        return []


@register
class CaaModule(BaseModule):
    name = "caa"
    description = "CAA Records Check"
    phase = 1
    step = 1

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        records = check_caa(domain)
        context.dns.caa_records = records

        if not records:
            return [Finding(
                id="CAA-001",
                module="caa",
                category="infrastructure",
                title="Keine CAA-Records — jede CA kann Zertifikate ausstellen",
                description=(
                    "Ohne CAA-Records (Certificate Authority Authorization) kann jede "
                    "Zertifizierungsstelle ein SSL-Zertifikat für diese Domain ausstellen. "
                    "CAA-Records schränken ein, welche CAs autorisiert sind."
                ),
                severity=Severity.LOW,
                evidence=f"dig CAA {domain} → Keine CAA-Records gefunden",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation=(
                    "CAA-Record anlegen, z.B.: {domain}. CAA 0 issue \"letsencrypt.org\" "
                    "um nur Let's Encrypt als CA zu autorisieren."
                ),
            )]
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.caa <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    records = check_caa(domain)
    if records:
        print(f"CAA records for {domain}:")
        for r in records:
            print(f"  {r}")
    else:
        print(f"No CAA records for {domain}")
