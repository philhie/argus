"""M03: IP Resolution & Cloud Provider Identification.

Maps discovered IPs to cloud providers (AWS, Azure, Hetzner, etc.)
using hardcoded CIDR ranges with reverse DNS fallback.

Usage: python -m argus.modules.ip_cloud_provider example.com
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from collections import Counter

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.ip_cloud_provider")

# (CIDR string, provider name) — pre-compiled at module load time
_CIDR_DEFS: list[tuple[str, str]] = [
    # AWS (major ranges)
    ("3.0.0.0/8", "AWS"),
    ("15.0.0.0/8", "AWS"),
    ("16.0.0.0/8", "AWS"),
    ("18.0.0.0/8", "AWS"),
    ("52.0.0.0/8", "AWS"),
    ("54.0.0.0/8", "AWS"),
    ("99.77.0.0/16", "AWS"),
    # Azure
    ("13.64.0.0/11", "Azure"),
    ("20.0.0.0/8", "Azure"),
    ("40.64.0.0/10", "Azure"),
    ("51.104.0.0/15", "Azure"),
    ("52.224.0.0/11", "Azure"),
    # Google Cloud
    ("34.0.0.0/8", "Google Cloud"),
    ("35.184.0.0/13", "Google Cloud"),
    ("104.196.0.0/14", "Google Cloud"),
    # Hetzner
    ("88.198.0.0/16", "Hetzner"),
    ("88.99.0.0/16", "Hetzner"),
    ("136.243.0.0/16", "Hetzner"),
    ("138.201.0.0/16", "Hetzner"),
    ("148.251.0.0/16", "Hetzner"),
    ("159.69.0.0/16", "Hetzner"),
    ("168.119.0.0/16", "Hetzner"),
    ("178.63.0.0/16", "Hetzner"),
    ("195.201.0.0/16", "Hetzner"),
    ("49.12.0.0/16", "Hetzner"),
    ("65.21.0.0/16", "Hetzner"),
    ("116.202.0.0/16", "Hetzner"),
    ("135.181.0.0/16", "Hetzner"),
    # IONOS (1&1)
    ("212.227.0.0/16", "IONOS"),
    ("217.160.0.0/16", "IONOS"),
    ("74.208.0.0/16", "IONOS"),
    # OVH
    ("51.68.0.0/16", "OVH"),
    ("51.77.0.0/16", "OVH"),
    ("51.91.0.0/16", "OVH"),
    ("51.75.0.0/16", "OVH"),
    ("51.38.0.0/16", "OVH"),
    ("54.36.0.0/16", "OVH"),
    ("54.37.0.0/16", "OVH"),
    ("54.38.0.0/16", "OVH"),
    # Strato
    ("81.169.128.0/17", "Strato"),
    ("85.214.0.0/15", "Strato"),
    # Oracle Cloud
    ("129.146.0.0/16", "Oracle Cloud"),
    ("129.151.0.0/16", "Oracle Cloud"),
    ("132.145.0.0/16", "Oracle Cloud"),
    ("140.238.0.0/16", "Oracle Cloud"),
    # DigitalOcean
    ("64.225.0.0/16", "DigitalOcean"),
    ("134.209.0.0/16", "DigitalOcean"),
    ("142.93.0.0/16", "DigitalOcean"),
    ("157.245.0.0/16", "DigitalOcean"),
    ("159.65.0.0/16", "DigitalOcean"),
    ("159.89.0.0/16", "DigitalOcean"),
    ("167.71.0.0/16", "DigitalOcean"),
    ("167.172.0.0/16", "DigitalOcean"),
    # Cloudflare
    ("104.16.0.0/12", "Cloudflare"),
    ("172.64.0.0/13", "Cloudflare"),
    ("188.114.96.0/20", "Cloudflare"),
    ("190.93.240.0/20", "Cloudflare"),
]

# Pre-compile networks for fast lookup
CLOUD_NETWORKS: list[tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, str]] = []
for _cidr, _provider in _CIDR_DEFS:
    try:
        CLOUD_NETWORKS.append((ipaddress.ip_network(_cidr, strict=False), _provider))
    except ValueError:
        pass

# Sort most-specific (longest prefix) first so /16 matches before /8
CLOUD_NETWORKS.sort(key=lambda pair: pair[0].prefixlen, reverse=True)

# Keywords in reverse DNS that hint at providers
_PTR_KEYWORDS: list[tuple[str, str]] = [
    ("amazonaws.com", "AWS"),
    ("azure", "Azure"),
    ("googleusercontent.com", "Google Cloud"),
    ("hetzner", "Hetzner"),
    ("ionos", "IONOS"),
    ("ovh", "OVH"),
    ("strato", "Strato"),
    ("oracle", "Oracle Cloud"),
    ("digitalocean", "DigitalOcean"),
    ("cloudflare", "Cloudflare"),
    ("linode", "Linode"),
]


def identify_provider(ip_str: str) -> str | None:
    """Match an IP against known cloud CIDR ranges."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return None

    for network, provider in CLOUD_NETWORKS:
        if addr in network:
            return provider
    return None


def reverse_dns_provider(ip_str: str) -> tuple[str | None, str | None]:
    """Attempt reverse DNS and match PTR record against known providers.

    Returns (provider_name_or_None, ptr_record_or_None).
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_str)
    except (socket.herror, socket.gaierror, OSError):
        return None, None

    lower = hostname.lower()
    for keyword, provider in _PTR_KEYWORDS:
        if keyword in lower:
            return provider, hostname
    return None, hostname


def scan_ip_cloud(context: ScanContext) -> list[Finding]:
    """Map discovered IPs to cloud providers."""
    findings: list[Finding] = []

    if not context.discovered_ips:
        logger.info("Keine IPs zum Auflösen — discovered_ips ist leer")
        return findings

    provider_map: dict[str, str] = {}  # ip → provider
    no_rdns_ips: list[str] = []

    for ip_str in sorted(context.discovered_ips):
        # Try CIDR match first
        provider = identify_provider(ip_str)

        if provider:
            provider_map[ip_str] = provider
            logger.debug(f"  {ip_str} → {provider} (CIDR)")
            continue

        # Fallback: reverse DNS
        rdns_provider, ptr = reverse_dns_provider(ip_str)
        if rdns_provider:
            provider_map[ip_str] = rdns_provider
            logger.debug(f"  {ip_str} → {rdns_provider} (rDNS: {ptr})")
        elif ptr is None:
            no_rdns_ips.append(ip_str)
            logger.debug(f"  {ip_str} → kein rDNS")
        else:
            logger.debug(f"  {ip_str} → unbekannt (rDNS: {ptr})")

    # Store in context for downstream modules
    context.cloud_providers = provider_map

    # Finding: Report each unique provider
    providers_seen = Counter(provider_map.values())
    for provider, count in providers_seen.most_common():
        ips_for_provider = [ip for ip, p in provider_map.items() if p == provider]
        findings.append(Finding(
            id=f"IP-001-{provider.replace(' ', '').upper()[:8]}",
            module="ip_cloud_provider",
            category="infrastructure",
            title=f"Cloud-Hosting erkannt: {provider}",
            description=(
                f"Die Domain wird bei {provider} gehostet "
                f"({count} IP{'s' if count > 1 else ''}: {', '.join(ips_for_provider[:5])}). "
                f"Cloud-Hosting ist an sich kein Sicherheitsproblem, aber relevant "
                f"für die Risikoanalyse gemäß NIS2."
            ),
            severity=Severity.INFO,
            evidence=f"CIDR/rDNS-Lookup: {', '.join(ips_for_provider[:5])} → {provider}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                f"Sicherstellen, dass die {provider}-Konfiguration den "
                f"Sicherheitsanforderungen entspricht (Shared Responsibility Model)."
            ),
        ))

    # Finding: Multiple providers
    unique_providers = list(providers_seen.keys())
    if len(unique_providers) >= 2:
        findings.append(Finding(
            id="IP-002",
            module="ip_cloud_provider",
            category="infrastructure",
            title=f"Mehrere Cloud-Provider im Einsatz ({len(unique_providers)})",
            description=(
                f"Die Infrastruktur verteilt sich auf {len(unique_providers)} verschiedene "
                f"Cloud-Provider: {', '.join(unique_providers)}. Multi-Cloud-Umgebungen "
                f"erhöhen die Komplexität der Sicherheitskonfiguration."
            ),
            severity=Severity.MEDIUM,
            evidence=f"Provider: {', '.join(unique_providers)}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                "Multi-Cloud-Sicherheitsstrategie dokumentieren. "
                "Einheitliche Sicherheitsrichtlinien über alle Provider hinweg sicherstellen."
            ),
        ))

    # Finding: No reverse DNS
    for ip in no_rdns_ips[:3]:  # Cap at 3 findings
        findings.append(Finding(
            id=f"IP-003-{ip.replace('.', '-')}",
            module="ip_cloud_provider",
            category="infrastructure",
            title=f"Kein Reverse-DNS für IP {ip}",
            description=(
                f"Für die IP-Adresse {ip} existiert kein Reverse-DNS-Eintrag (PTR-Record). "
                f"Dies kann auf eine unzureichende Netzwerkkonfiguration hindeuten."
            ),
            severity=Severity.LOW,
            evidence=f"rDNS-Lookup für {ip} fehlgeschlagen (kein PTR-Record)",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=f"PTR-Record für {ip} beim Hosting-Provider einrichten.",
        ))

    return findings


@register
class IpCloudProviderModule(BaseModule):
    name = "ip_cloud_provider"
    description = "IP Resolution & Cloud Provider Identification"
    phase = 1
    step = 1  # Same as dns_intel; runs after it alphabetically

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_ip_cloud(context)


if __name__ == "__main__":
    import sys
    import dns.resolver

    logging.basicConfig(level=logging.DEBUG)
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"

    ctx = ScanContext(domain=target)
    # Resolve A records
    try:
        answers = dns.resolver.resolve(target, "A")
        for answer in answers:
            ctx.discovered_ips.add(str(answer))
    except Exception as e:
        print(f"DNS-Auflösung fehlgeschlagen: {e}")
        sys.exit(1)

    print(f"IPs: {', '.join(sorted(ctx.discovered_ips))}")
    results = scan_ip_cloud(ctx)
    print(f"\n{len(results)} Findings:")
    for f in results:
        print(f"  [{f.severity.value}] {f.title}")
        print(f"    {f.evidence}")
    print(f"\nProvider-Map: {ctx.cloud_providers}")
