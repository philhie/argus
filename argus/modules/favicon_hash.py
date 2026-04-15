"""M27: Favicon Hash → Hidden Infrastructure Discovery.

Downloads the favicon from a domain, computes the mmh3 hash (Shodan-compatible),
and searches Shodan for all hosts sharing that favicon to discover hidden/shadow
infrastructure.

Usage: python -m argus.modules.favicon_hash example.de
"""

from __future__ import annotations

import codecs
import logging

import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.favicon_hash")

DEV_STAGING_KEYWORDS = {"dev", "staging", "test", "internal"}


def _download_favicon(domain: str) -> bytes | None:
    """Download favicon.ico from domain. Returns bytes or None."""
    url = f"https://{domain}/favicon.ico"
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return None
        if len(resp.content) < 100:
            logger.debug("Favicon zu klein (%d Bytes), übersprungen", len(resp.content))
            return None
        return resp.content
    except requests.RequestException as exc:
        logger.debug("Favicon-Download fehlgeschlagen für %s: %s", domain, exc)
        return None


def _compute_favicon_hash(favicon_bytes: bytes) -> int:
    """Compute the Shodan-compatible mmh3 favicon hash."""
    try:
        import mmh3
    except ImportError:
        logger.info("mmh3 nicht installiert — Favicon-Hash-Modul übersprungen")
        raise
    return mmh3.hash(codecs.encode(favicon_bytes, "base64"))


def _search_shodan(favicon_hash: int) -> list[dict]:
    """Search Shodan for hosts with the given favicon hash."""
    try:
        import shodan
    except ImportError:
        logger.info("shodan nicht installiert — Shodan-Suche übersprungen")
        raise

    api = shodan.Shodan(settings.shodan_api_key)
    try:
        results = api.search(f"http.favicon.hash:{favicon_hash}")
        return results.get("matches", [])
    except shodan.APIError as exc:
        logger.warning("Shodan-API-Fehler: %s", exc)
        return []


def check_favicon_hash(domain: str, context: ScanContext) -> list[Finding]:
    """Download favicon, hash it, search Shodan, analyse results."""
    findings: list[Finding] = []

    # Gate: Shodan API key required
    if not settings.shodan_api_key:
        logger.info("Kein Shodan-API-Key konfiguriert — Favicon-Hash-Modul übersprungen")
        return findings

    # Import check (mmh3 + shodan)
    try:
        import mmh3  # noqa: F401
        import shodan  # noqa: F401
    except ImportError:
        return findings

    # Download favicon
    favicon_bytes = _download_favicon(domain)
    if favicon_bytes is None:
        return findings

    # Compute hash
    try:
        favicon_hash = _compute_favicon_hash(favicon_bytes)
    except ImportError:
        return findings

    logger.info("Favicon-Hash für %s: %d", domain, favicon_hash)

    # Search Shodan
    matches = _search_shodan(favicon_hash)
    if not matches:
        return findings

    # Analyse results
    known_ips = context.discovered_ips or set()
    hidden_hosts: list[dict] = []
    unexpected_network_hosts: list[dict] = []
    dev_staging_hosts: list[dict] = []

    for match in matches:
        ip = match.get("ip_str", "")
        hostnames = match.get("hostnames", [])
        org = match.get("org", "")
        asn = match.get("asn", "")

        # Check for dev/staging indicators in hostnames
        for hostname in hostnames:
            hostname_lower = hostname.lower()
            for keyword in DEV_STAGING_KEYWORDS:
                if keyword in hostname_lower:
                    dev_staging_hosts.append({
                        "ip": ip,
                        "hostname": hostname,
                        "org": org,
                        "asn": asn,
                    })
                    break

        # Hidden host: IP not in known set
        if ip and ip not in known_ips:
            hidden_hosts.append({
                "ip": ip,
                "hostnames": hostnames,
                "org": org,
                "asn": asn,
                "port": match.get("port"),
            })

            # Check for unexpected network/ASN
            # If the host org differs from the majority of known hosts, flag it
            if org and context.shodan_hosts:
                known_orgs = {h.get("org", "") for h in context.shodan_hosts if h.get("org")}
                if known_orgs and org not in known_orgs:
                    unexpected_network_hosts.append({
                        "ip": ip,
                        "hostnames": hostnames,
                        "org": org,
                        "asn": asn,
                    })

    # Store discovered hosts in context
    for host in hidden_hosts:
        context.shodan_hosts.append({
            "ip": host["ip"],
            "hostnames": host.get("hostnames", []),
            "org": host.get("org", ""),
            "asn": host.get("asn", ""),
            "port": host.get("port"),
            "source": "favicon_hash",
        })

    # FAV-001: Hidden hosts sharing favicon not in known IPs
    if hidden_hosts:
        n = len(hidden_hosts)
        ip_list = ", ".join(h["ip"] for h in hidden_hosts[:10])
        evidence_extra = f" (und {n - 10} weitere)" if n > 10 else ""
        findings.append(Finding(
            id="FAV-001",
            module="favicon_hash",
            category="infrastructure",
            title=f"{n} unbekannte Hosts mit identischem Favicon-Hash",
            description=(
                f"Der Favicon-Hash ({favicon_hash}) wurde auf {n} Host(s) gefunden, "
                f"die nicht zur bekannten Infrastruktur gehören. Diese Hosts könnten "
                f"vergessene, interne oder Shadow-IT-Systeme sein, die dasselbe "
                f"Branding verwenden."
            ),
            severity=Severity.HIGH,
            evidence=f"Favicon-Hash: {favicon_hash} → IPs: {ip_list}{evidence_extra}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                "Alle identifizierten Hosts überprüfen und dokumentieren. "
                "Nicht autorisierte Systeme abschalten oder in das Asset-Management aufnehmen."
            ),
        ))

    # FAV-002: Hosts on unexpected network/ASN
    if unexpected_network_hosts:
        host_details = "; ".join(
            f"{h['ip']} ({h['org']})" for h in unexpected_network_hosts[:5]
        )
        findings.append(Finding(
            id="FAV-002",
            module="favicon_hash",
            category="infrastructure",
            title="Favicon-Match auf unerwartetem Netzwerk",
            description=(
                "Hosts mit identischem Favicon wurden in Netzwerken/ASNs gefunden, "
                "die nicht der bekannten Infrastruktur zugeordnet sind. Dies kann auf "
                "ausgelagerte Systeme, Schatten-IT oder kompromittierte Instanzen hinweisen."
            ),
            severity=Severity.MEDIUM,
            evidence=f"Unerwartete Netzwerke: {host_details}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                "Prüfen, ob die identifizierten Hosts legitimerweise Ihr Favicon verwenden. "
                "Ggf. Hosting-Vereinbarungen und Drittanbieter-Deployments überprüfen."
            ),
        ))

    # FAV-003: Dev/staging hosts discovered
    for host in dev_staging_hosts:
        hostname = host["hostname"]
        findings.append(Finding(
            id="FAV-003",
            module="favicon_hash",
            category="infrastructure",
            title=f"Potentieller Dev/Staging-Server via Favicon-Hash entdeckt: {hostname}",
            description=(
                f"Der Host {hostname} ({host['ip']}) verwendet dasselbe Favicon "
                f"und enthält Schlüsselwörter (dev, staging, test, internal), "
                f"die auf eine Entwicklungs- oder Testumgebung hindeuten. "
                f"Solche Systeme sind häufig weniger geschützt."
            ),
            severity=Severity.HIGH,
            evidence=f"Hostname: {hostname}, IP: {host['ip']}, Org: {host['org']}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
            remediation=(
                "Dev/Staging-Systeme dürfen nicht öffentlich erreichbar sein. "
                "Zugang über VPN oder IP-Whitelist beschränken und vom Internet isolieren."
            ),
        ))

    return findings


@register
class FaviconHashModule(BaseModule):
    name = "favicon_hash"
    description = "Favicon Hash → Hidden Infrastructure"
    phase = 3
    step = 4

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_favicon_hash(domain, context)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.favicon_hash <domain>")
        sys.exit(1)

    target = sys.argv[1]
    if target.startswith("http"):
        target = target.split("//", 1)[1].split("/")[0]
    print(f"Checking favicon hash for {target}...")

    ctx = ScanContext(domain=target)
    results = check_favicon_hash(target, ctx)
    for f in results:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(results)} findings")
