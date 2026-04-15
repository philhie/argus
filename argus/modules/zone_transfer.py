"""M26: DNS Zone Transfer (AXFR) Test.

Usage: python -m argus.modules.zone_transfer true-fruits.com
"""

from __future__ import annotations

import logging

import dns.query
import dns.rdatatype
import dns.zone

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.zone_transfer")


def check_zone_transfer(domain: str, ns_records: list[str]) -> tuple[bool, list[dict]]:
    """Attempt AXFR against all nameservers. Returns (vulnerable, records)."""
    for ns in ns_records:
        try:
            zone = dns.zone.from_xfr(
                dns.query.xfr(ns, domain, timeout=10)
            )
            records = []
            for name, node in zone.nodes.items():
                for rdataset in node.rdatasets:
                    for rdata in rdataset:
                        records.append({
                            "name": str(name),
                            "type": dns.rdatatype.to_text(rdataset.rdtype),
                            "value": str(rdata),
                            "ttl": rdataset.ttl,
                        })
            return True, records
        except Exception:
            continue
    return False, []


@register
class ZoneTransferModule(BaseModule):
    name = "zone_transfer"
    description = "DNS Zone Transfer (AXFR) Test"
    phase = 1
    step = 1

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        from argus.config import settings
        if not settings.enable_axfr:
            logger.debug("AXFR test disabled via config")
            return []

        ns_records = context.dns.ns_records
        if not ns_records:
            logger.info("No NS records available, skipping zone transfer test")
            return []

        vulnerable, records = check_zone_transfer(domain, ns_records)
        context.dns.zone_transfer_vulnerable = vulnerable
        context.dns.zone_transfer_records = records

        if vulnerable:
            record_count = len(records)
            sample = ", ".join(
                f"{r['name']}.{domain} ({r['type']})"
                for r in records[:5]
            )
            return [Finding(
                id="DNS-AXFR",
                module="zone_transfer",
                category="infrastructure",
                title="DNS Zone Transfer (AXFR) erlaubt — komplette DNS-Zone offengelegt",
                description=(
                    f"Der Nameserver erlaubt Zone Transfers. Ein Angreifer erhält mit "
                    f"einem einzigen Befehl alle {record_count} DNS-Records — jede Subdomain, "
                    f"jeden internen Hostnamen, jeden MX- und SRV-Record."
                ),
                severity=Severity.CRITICAL,
                evidence=(
                    f"dig AXFR {domain} @{ns_records[0]} → "
                    f"{record_count} Records erhalten. Beispiele: {sample}"
                ),
                nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 9"],
                remediation="Zone Transfers auf allen Nameservern auf autorisierte Secondary-NS beschränken.",
            )]
        return []


if __name__ == "__main__":
    import sys

    import dns.resolver

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.zone_transfer <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Testing zone transfer for {domain}...")

    try:
        ns_answers = dns.resolver.resolve(domain, 'NS')
        ns_records = [str(r).rstrip('.') for r in ns_answers]
    except Exception:
        print("Could not resolve NS records")
        sys.exit(1)

    vulnerable, records = check_zone_transfer(domain, ns_records)
    if vulnerable:
        print(f"VULNERABLE! Got {len(records)} records")
        for r in records[:10]:
            print(f"  {r['name']} {r['type']} {r['value']}")
    else:
        print("Not vulnerable (AXFR denied on all nameservers)")
