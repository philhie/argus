"""M02: Subdomain Discovery — crt.sh Certificate Transparency + DNS brute force.

Usage: python -m argus.modules.subdomain_discovery true-fruits.com
"""

from __future__ import annotations

import logging
from typing import Optional

import dns.resolver
import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.subdomain_discovery")

# ~100 common subdomains including German Mittelstand-relevant names
SUBDOMAIN_WORDLIST = [
    "www", "mail", "smtp", "pop", "imap", "ftp", "vpn", "remote", "owa", "webmail",
    "autodiscover", "lyncdiscover", "sip", "adfs", "fs", "sso", "portal",
    "intranet", "intern", "extranet", "sharepoint", "teams",
    "admin", "administrator", "panel", "cpanel", "plesk",
    "dev", "staging", "test", "qa", "uat", "sandbox", "demo", "beta", "preview",
    "api", "app", "mobile", "cdn", "static", "media", "assets", "files", "upload",
    "old", "legacy", "archive", "backup", "bak",
    "shop", "store", "www2", "www3", "web",
    "gitlab", "jenkins", "jira", "confluence", "wiki", "docs",
    "monitoring", "grafana", "kibana", "elastic", "prometheus",
    "db", "database", "mysql", "postgres", "redis", "mongo",
    "citrix", "terminal", "rdp", "ts", "gateway",
    "exchange", "mx", "mx1", "mx2", "ns1", "ns2",
]

# Finding classification sets
DEV_STAGING_NAMES = {"dev", "staging", "test", "qa", "uat", "sandbox", "demo", "beta", "preview"}
ADMIN_PANEL_NAMES = {"admin", "administrator", "panel", "cpanel", "plesk"}
VPN_REMOTE_NAMES = {"vpn", "remote", "citrix"}
DATABASE_NAMES = {"db", "database", "mysql", "postgres", "redis", "mongo"}


def _make_resolver() -> dns.resolver.Resolver:
    """Create a DNS resolver with sensible defaults."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.timeout = 5
    resolver.lifetime = 10
    return resolver


def _resolve_a(fqdn: str, resolver: dns.resolver.Resolver) -> list[str]:
    """Resolve a FQDN to A record IPs. Returns empty list on failure."""
    try:
        answers = resolver.resolve(fqdn, "A")
        return [str(rdata) for rdata in answers]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers, dns.exception.Timeout,
            dns.resolver.LifetimeTimeout):
        return []
    except Exception as e:
        logger.debug("DNS A query for %s failed: %s", fqdn, e)
        return []


def _check_wildcard(domain: str, resolver: dns.resolver.Resolver) -> bool:
    """Detect wildcard DNS by querying a random-looking subdomain."""
    canary = f"xz9q7rand0mcheck42.{domain}"
    ips = _resolve_a(canary, resolver)
    return len(ips) > 0


def _query_crtsh(domain: str) -> set[str]:
    """Query crt.sh Certificate Transparency logs for subdomains."""
    subdomains: set[str] = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        entries = resp.json()
    except requests.exceptions.Timeout:
        logger.warning("crt.sh request timed out after 30s — skipping CT data")
        return subdomains
    except Exception as e:
        logger.warning("crt.sh query failed: %s — continuing with DNS brute force", e)
        return subdomains

    for entry in entries:
        name_value = entry.get("name_value", "")
        # name_value can contain multiple newline-separated names
        for name in name_value.split("\n"):
            name = name.strip().lower()
            # Strip wildcard prefix
            if name.startswith("*."):
                name = name[2:]
            # Only keep subdomains of our target domain
            if name.endswith(f".{domain}") or name == domain:
                subdomains.add(name)

    logger.info("crt.sh returned %d unique subdomains for %s", len(subdomains), domain)
    return subdomains


def _bruteforce_subdomains(domain: str, resolver: dns.resolver.Resolver) -> set[str]:
    """Brute-force common subdomains via DNS resolution."""
    found: set[str] = set()
    for sub in SUBDOMAIN_WORDLIST:
        fqdn = f"{sub}.{domain}"
        ips = _resolve_a(fqdn, resolver)
        if ips:
            found.add(fqdn)
            logger.debug("Brute-force hit: %s → %s", fqdn, ips)
    logger.info("DNS brute force found %d live subdomains for %s", len(found), domain)
    return found


def scan_subdomains(
    domain: str,
) -> tuple[list[str], dict[str, list[str]], list[Finding]]:
    """Discover subdomains and resolve them.

    Returns:
        all_subdomains: sorted list of all discovered subdomains
        resolved: mapping of subdomain → list of IPs (only those that resolved)
        findings: security findings
    """
    resolver = _make_resolver()
    findings: list[Finding] = []

    # --- Step 1: Detect wildcard DNS ---
    wildcard = _check_wildcard(domain, resolver)
    if wildcard:
        logger.warning("Wildcard DNS detected for %s — results may contain false positives", domain)
        findings.append(Finding(
            id="SUB-006",
            module="subdomain_discovery",
            category="infrastructure",
            title="Wildcard-DNS erkannt",
            description=(
                f"Die Domain {domain} verwendet Wildcard-DNS. Jeder beliebige "
                "Subdomain-Name löst zu einer IP-Adresse auf. Dies kann die "
                "Subdomain-Enumeration verfälschen und wird manchmal eingesetzt, "
                "um Angreifer zu verwirren."
            ),
            severity=Severity.INFO,
            evidence=f"Zufällige Subdomain xz9q7rand0mcheck42.{domain} löst zu einer IP auf",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation="Wildcard-DNS-Einträge prüfen und ggf. entfernen.",
        ))

    # --- Step 2: crt.sh Certificate Transparency ---
    ct_subdomains = _query_crtsh(domain)

    # --- Step 3: DNS brute force (if enabled) ---
    bruteforce_subdomains: set[str] = set()
    if getattr(settings, "enable_subdomain_bruteforce", True):
        bruteforce_subdomains = _bruteforce_subdomains(domain, resolver)

    # Merge all discovered subdomains
    all_candidates = ct_subdomains | bruteforce_subdomains

    # --- Step 4: Resolve each subdomain ---
    resolved: dict[str, list[str]] = {}
    for sub in sorted(all_candidates):
        if sub == domain:
            continue  # Skip the apex domain itself
        ips = _resolve_a(sub, resolver)
        if ips:
            resolved[sub] = ips

    all_subdomains = sorted(resolved.keys())
    live_count = len(all_subdomains)
    logger.info(
        "Subdomain discovery complete: %d candidates, %d live for %s",
        len(all_candidates), live_count, domain,
    )

    # --- Step 5: Generate findings ---
    for sub in all_subdomains:
        # Extract the leftmost label to classify
        prefix = sub.replace(f".{domain}", "").split(".")[0].lower()

        if prefix in DEV_STAGING_NAMES:
            findings.append(Finding(
                id="SUB-001",
                module="subdomain_discovery",
                category="infrastructure",
                title=f"Entwicklungs-/Staging-Subdomain öffentlich erreichbar: {sub}",
                description=(
                    f"Die Subdomain {sub} ist öffentlich über DNS auflösbar. "
                    "Entwicklungs- und Testumgebungen enthalten häufig Schwachstellen, "
                    "Debug-Informationen oder schwache Zugangsdaten."
                ),
                severity=Severity.MEDIUM,
                evidence=f"DNS A-Record: {sub} → {', '.join(resolved[sub])}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=(
                    "Entwicklungs-Subdomains nicht öffentlich auflösbar machen oder "
                    "Zugriff per VPN/IP-Whitelist einschränken."
                ),
            ))

        elif prefix in ADMIN_PANEL_NAMES:
            findings.append(Finding(
                id="SUB-002",
                module="subdomain_discovery",
                category="infrastructure",
                title=f"Admin-Panel-Subdomain öffentlich erreichbar: {sub}",
                description=(
                    f"Die Subdomain {sub} deutet auf ein öffentlich erreichbares "
                    "Administrations-Panel hin. Admin-Panels sind bevorzugte Ziele "
                    "für Brute-Force-Angriffe und sollten nicht öffentlich zugänglich sein."
                ),
                severity=Severity.HIGH,
                evidence=f"DNS A-Record: {sub} → {', '.join(resolved[sub])}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
                remediation=(
                    "Admin-Panels hinter VPN oder IP-Whitelist betreiben. "
                    "Multi-Faktor-Authentifizierung aktivieren."
                ),
            ))

        elif prefix in VPN_REMOTE_NAMES:
            findings.append(Finding(
                id="SUB-003",
                module="subdomain_discovery",
                category="infrastructure",
                title=f"VPN-/Remote-Access-Subdomain entdeckt: {sub}",
                description=(
                    f"Die Subdomain {sub} weist auf einen Remote-Access-Dienst hin. "
                    "Dies ist eine normale Infrastrukturkomponente, sollte aber regelmäßig "
                    "auf Sicherheitsupdates und Konfiguration geprüft werden."
                ),
                severity=Severity.INFO,
                evidence=f"DNS A-Record: {sub} → {', '.join(resolved[sub])}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=(
                    "VPN-/Remote-Access-Software regelmäßig aktualisieren. "
                    "Multi-Faktor-Authentifizierung sicherstellen."
                ),
            ))

        elif prefix in DATABASE_NAMES:
            findings.append(Finding(
                id="SUB-004",
                module="subdomain_discovery",
                category="infrastructure",
                title=f"Datenbank-Subdomain öffentlich erreichbar: {sub}",
                description=(
                    f"Die Subdomain {sub} deutet auf einen öffentlich erreichbaren "
                    "Datenbankdienst hin. Datenbanken sollten niemals direkt aus dem "
                    "Internet erreichbar sein."
                ),
                severity=Severity.HIGH,
                evidence=f"DNS A-Record: {sub} → {', '.join(resolved[sub])}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=(
                    "Datenbank-Server nicht öffentlich auflösbar machen. "
                    "Zugriff ausschließlich über interne Netzwerke oder VPN erlauben."
                ),
            ))

    # Large attack surface finding
    if live_count > 20:
        findings.append(Finding(
            id="SUB-005",
            module="subdomain_discovery",
            category="infrastructure",
            title=f"Große Angriffsfläche: {live_count} aktive Subdomains entdeckt",
            description=(
                f"Es wurden {live_count} aktive Subdomains für {domain} gefunden. "
                "Eine große Anzahl öffentlich erreichbarer Subdomains erhöht die "
                "Angriffsfläche und erschwert die Wartung aller Systeme."
            ),
            severity=Severity.INFO,
            evidence=f"{live_count} aktive Subdomains gefunden (Schwellenwert: 20)",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                "Regelmäßige Subdomain-Inventur durchführen. Nicht mehr benötigte "
                "Subdomains und DNS-Einträge entfernen."
            ),
        ))

    return all_subdomains, resolved, findings


@register
class SubdomainDiscoveryModule(BaseModule):
    name = "subdomain_discovery"
    description = "Subdomain Discovery (crt.sh + DNS)"
    phase = 3
    step = 5

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        all_subdomains, resolved, findings = scan_subdomains(domain)

        # Populate context
        context.subdomains = all_subdomains
        for ips in resolved.values():
            for ip in ips:
                context.discovered_ips.add(ip)

        return findings


# Standalone execution
if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.subdomain_discovery <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Discovering subdomains for {domain}...")
    all_subdomains, resolved, findings = scan_subdomains(domain)

    print(f"\n{'='*60}")
    print(f"Subdomain Discovery Results for {domain}")
    print(f"{'='*60}")
    print(f"Total discovered: {len(all_subdomains)}")
    print(f"Live (resolved):  {len(resolved)}")
    print()

    for sub in all_subdomains:
        ips = resolved.get(sub, [])
        print(f"  {sub:50s} → {', '.join(ips)}")

    print(f"\n{'='*60}")
    print(f"Findings ({len(findings)})")
    print(f"{'='*60}")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()
