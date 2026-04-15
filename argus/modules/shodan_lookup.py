"""M04: Shodan Infrastructure Enumeration — open ports, services, CVEs.

Primary data source: Shodan InternetDB (free, no auth, unlimited).
Optional enrichment: Shodan paid API (CVSS scores, OS detection, service banners).

Usage: python -m argus.modules.shodan_lookup <domain>
"""

from __future__ import annotations

import logging
import re
import time

import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.shodan_lookup")

HIGH_RISK_PORTS = {
    21: ("FTP", Severity.HIGH),
    23: ("Telnet", Severity.CRITICAL),
    445: ("SMB", Severity.HIGH),
    1433: ("MSSQL", Severity.CRITICAL),
    3306: ("MySQL", Severity.CRITICAL),
    3389: ("RDP", Severity.CRITICAL),
    5432: ("PostgreSQL", Severity.CRITICAL),
    5900: ("VNC", Severity.HIGH),
    6379: ("Redis", Severity.CRITICAL),
    27017: ("MongoDB", Severity.CRITICAL),
    9200: ("Elasticsearch", Severity.HIGH),
    11211: ("Memcached", Severity.HIGH),
}

# OS strings that indicate end-of-life / outdated systems
EOL_OS_PATTERNS = [
    "Windows XP",
    "Windows 7",
    "Windows Server 2003",
    "Windows Server 2008",
    "Windows Server 2012",
    "Ubuntu 14.",
    "Ubuntu 16.",
    "Debian 8",
    "Debian 9",
    "CentOS 6",
    "CentOS 7",
]

# Regex to extract product and version from CPE 2.2/2.3 strings
# e.g. "cpe:/a:apache:http_server:2.4.51" or "cpe:2.3:a:apache:http_server:2.4.51:*:*:*:*:*:*:*"
_CPE_RE = re.compile(
    r"cpe:(?:/|2\.3:)[aho]:([^:]+):([^:]+):([^:*]+)",
)


def _is_eol_os(os_string: str) -> bool:
    """Check if an OS string matches known EOL patterns."""
    if not os_string:
        return False
    for pattern in EOL_OS_PATTERNS:
        if pattern.lower() in os_string.lower():
            return True
    return False


def _severity_for_cvss(cvss: float) -> Severity:
    """Map CVSS score to severity level."""
    if cvss >= 9.0:
        return Severity.CRITICAL
    if cvss >= 7.0:
        return Severity.HIGH
    return Severity.MEDIUM


def _parse_cpes(cpes: list[str]) -> dict[str, str]:
    """Parse CPE strings into {product: version} dict."""
    result: dict[str, str] = {}
    for cpe in cpes:
        m = _CPE_RE.search(cpe)
        if m:
            vendor, product, version = m.group(1), m.group(2), m.group(3)
            # Clean up underscore-separated names
            name = product.replace("_", " ").title()
            result[name] = version
    return result


def _query_internetdb(ip: str) -> dict | None:
    """Query Shodan InternetDB (free, no auth, unlimited).

    Returns dict with keys: ip, ports, hostnames, cpes, vulns, tags.
    Returns None if no data available or on error.
    """
    try:
        resp = requests.get(
            f"https://internetdb.shodan.io/{ip}",
            timeout=10,
            headers={"User-Agent": "KENGO-ARGUS-Scanner"},
        )
        if resp.status_code == 404:
            logger.debug("InternetDB: Keine Daten für %s", ip)
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.debug("InternetDB-Abfrage fehlgeschlagen für %s: %s", ip, e)
        return None


def _enrich_with_paid_api(ip: str) -> dict | None:
    """Optionally enrich with paid Shodan API for CVSS, OS, banners."""
    if not settings.shodan_api_key:
        return None

    try:
        import shodan
    except ImportError:
        return None

    api = shodan.Shodan(settings.shodan_api_key)
    try:
        return api.host(ip)
    except shodan.APIError as e:
        error_msg = str(e)
        if "No information available" in error_msg:
            logger.debug("Shodan API: Keine Daten für %s", ip)
        elif "429" in error_msg or "Too Many Requests" in error_msg:
            logger.warning("Shodan API Rate-Limit erreicht — Enrichment gestoppt")
            raise  # Let caller know to stop enrichment
        else:
            logger.debug("Shodan API-Fehler für %s: %s", ip, error_msg)
        return None
    except Exception as e:
        logger.debug("Shodan API-Fehler für %s: %s", ip, e)
        return None


def scan_shodan(context: ScanContext) -> list[Finding]:
    """Query InternetDB (free) for each IP, optionally enrich with paid Shodan API."""
    findings: list[Finding] = []

    ips = sorted(context.discovered_ips)
    if not ips:
        logger.info("Keine IPs zum Abfragen — discovered_ips ist leer")
        return findings

    logger.info("InternetDB-Abfrage für %d IP(s): %s", len(ips), ", ".join(ips))

    enrich_with_paid = bool(settings.shodan_api_key)
    stop_enrichment = False  # Set to True if paid API rate-limited

    for ip in ips:
        # --- Primary: InternetDB (free, unlimited) ---
        idb = _query_internetdb(ip)
        if idb is None:
            continue

        ports = idb.get("ports", [])
        vulns = idb.get("vulns", [])  # List of CVE ID strings
        hostnames = idb.get("hostnames", [])
        cpes = idb.get("cpes", [])
        tags = idb.get("tags", [])

        # Parse CPEs into product/version pairs
        software = _parse_cpes(cpes)

        # --- Optional: Paid API enrichment ---
        paid_data: dict | None = None
        cvss_map: dict[str, float] = {}
        os_info = ""
        services: dict[int, dict] = {}

        if enrich_with_paid and not stop_enrichment:
            time.sleep(1.1)  # Rate limit for paid API
            try:
                paid_data = _enrich_with_paid_api(ip)
            except Exception:
                stop_enrichment = True  # 429 — stop trying paid API

            if paid_data:
                os_info = paid_data.get("os") or ""
                # Build CVSS map from paid data
                paid_vulns = paid_data.get("vulns", {})
                if isinstance(paid_vulns, dict):
                    for cve_id, cve_data in paid_vulns.items():
                        if isinstance(cve_data, dict):
                            cvss_map[cve_id] = float(cve_data.get("cvss", 0) or 0)
                        elif isinstance(cve_data, (int, float)):
                            cvss_map[cve_id] = float(cve_data)
                # Build service map from banners
                for banner in paid_data.get("data", []):
                    port = banner.get("port")
                    if port is not None:
                        services[port] = {
                            "service": banner.get("product") or banner.get("_shodan", {}).get("module", "unknown"),
                            "version": banner.get("version") or "",
                        }

        # --- Store in context ---
        host_entry = {
            "ip": ip,
            "ports": sorted(ports),
            "services": services,
            "vulns": vulns,
            "os": os_info,
            "hostnames": hostnames,
            "cpes": cpes,
            "software": software,
            "tags": tags,
            "source": "internetdb" + ("+shodan" if paid_data else ""),
        }
        context.shodan_hosts.append(host_entry)

        # --- SHO-001: High-risk ports ---
        for port in ports:
            if port in HIGH_RISK_PORTS:
                service_name, severity = HIGH_RISK_PORTS[port]
                # Try to get version from paid API or CPE
                svc = services.get(port, {})
                version_str = svc.get("version", "")
                detail = f" (v{version_str})" if version_str else ""

                findings.append(Finding(
                    id="SHO-001",
                    module="shodan_lookup",
                    category="infrastructure",
                    title=f"{service_name} öffentlich erreichbar auf {ip}:{port}",
                    description=(
                        f"Der Dienst {service_name}{detail} ist auf Port {port} "
                        f"öffentlich aus dem Internet erreichbar. "
                        f"Dieser Dienst sollte nicht ohne VPN oder Firewall-Regeln "
                        f"exponiert sein, da er ein häufiges Angriffsziel darstellt."
                    ),
                    severity=severity,
                    evidence=f"InternetDB {ip} → Port {port} offen ({service_name})",
                    nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                    remediation=(
                        f"Port {port} ({service_name}) mit einer Firewall einschränken "
                        f"oder hinter ein VPN legen. Wenn der Dienst nicht benötigt wird, "
                        f"deaktivieren."
                    ),
                ))

        # --- SHO-002: Known CVEs ---
        for cve_id in vulns:
            cvss = cvss_map.get(cve_id, 0.0)
            if cvss > 0:
                severity = _severity_for_cvss(cvss)
                cvss_str = f" (CVSS {cvss:.1f})"
            else:
                # No CVSS from paid API — default to HIGH
                severity = Severity.HIGH
                cvss_str = ""

            findings.append(Finding(
                id="SHO-002",
                module="shodan_lookup",
                category="infrastructure",
                title=f"{cve_id} auf {ip}{cvss_str}",
                description=(
                    f"Die bekannte Schwachstelle {cve_id}{cvss_str} wurde "
                    f"auf {ip} erkannt. Dieser Host ist angreifbar und "
                    f"sollte umgehend gepatcht werden."
                ),
                severity=severity,
                evidence=f"InternetDB {ip} → vulns enthält {cve_id}",
                cvss_score=cvss if cvss > 0 else None,
                cve_ids=[cve_id],
                nis2_paragraphs=["§30 Abs. 2 Nr. 5"],
                remediation=(
                    f"Sicherheitsupdate für {cve_id} einspielen. "
                    f"Prüfen Sie die Herstellerseite für verfügbare Patches."
                ),
            ))

        # --- SHO-003: Outdated/EOL OS (paid API only) ---
        if os_info and _is_eol_os(os_info):
            findings.append(Finding(
                id="SHO-003",
                module="shodan_lookup",
                category="infrastructure",
                title=f"Veraltetes Betriebssystem: {os_info}",
                description=(
                    f"Das Betriebssystem '{os_info}' auf {ip} ist veraltet und "
                    f"erhält keine Sicherheitsupdates mehr (End of Life). "
                    f"Systeme ohne Sicherheitsupdates sind besonders anfällig für "
                    f"bekannte Schwachstellen."
                ),
                severity=Severity.HIGH,
                evidence=f"Shodan API {ip} → os: {os_info}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=(
                    f"Das Betriebssystem auf eine aktuelle, unterstützte Version "
                    f"migrieren. Falls ein sofortiges Update nicht möglich ist, "
                    f"das System vom Internet isolieren."
                ),
            ))

        # --- SHO-004: Excessive open ports ---
        if len(ports) > 10:
            findings.append(Finding(
                id="SHO-004",
                module="shodan_lookup",
                category="infrastructure",
                title=f"{len(ports)} offene Ports auf {ip}",
                description=(
                    f"Auf {ip} sind {len(ports)} Ports öffentlich erreichbar. "
                    f"Eine große Anzahl offener Ports erhöht die Angriffsfläche "
                    f"erheblich und deutet auf eine unzureichende "
                    f"Firewall-Konfiguration hin."
                ),
                severity=Severity.MEDIUM,
                evidence=(
                    f"InternetDB {ip} → {len(ports)} offene Ports: "
                    f"{', '.join(str(p) for p in sorted(ports)[:20])}"
                    f"{'...' if len(ports) > 20 else ''}"
                ),
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=(
                    "Alle nicht benötigten Dienste deaktivieren und Firewall-Regeln "
                    "verschärfen. Nur die tatsächlich benötigten Ports freigeben."
                ),
            ))

    logger.info(
        "Shodan-Abfrage abgeschlossen: %d Host(s), %d Finding(s)%s",
        len(context.shodan_hosts),
        len(findings),
        " (mit Paid-API-Enrichment)" if enrich_with_paid and not stop_enrichment else "",
    )

    return findings


@register
class ShodanLookupModule(BaseModule):
    name = "shodan_lookup"
    description = "Shodan Infrastructure Enumeration"
    phase = 3
    step = 4

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_shodan(context)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.shodan_lookup <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Shodan-Lookup für {domain}...")

    # Minimal context setup: resolve IPs via DNS first
    ctx = ScanContext(domain=domain)

    try:
        import dns.resolver

        resolver = dns.resolver.Resolver()
        resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
        resolver.timeout = 5
        resolver.lifetime = 10

        for answer in resolver.resolve(domain, "A"):
            ctx.discovered_ips.add(str(answer))
        print(f"Gefundene IPs: {', '.join(sorted(ctx.discovered_ips))}")
    except Exception as e:
        print(f"DNS-Auflösung fehlgeschlagen: {e}")
        print("Bitte IPs manuell angeben oder dns_intel zuerst ausführen.")
        sys.exit(1)

    findings = scan_shodan(ctx)

    print(f"\n{'='*60}")
    print(f"Shodan-Ergebnisse für {domain}")
    print(f"{'='*60}")

    for host_data in ctx.shodan_hosts:
        print(f"\n  IP: {host_data['ip']}")
        print(f"  Source: {host_data['source']}")
        print(f"  Ports: {host_data['ports']}")
        print(f"  Hostnames: {host_data['hostnames']}")
        print(f"  CVEs: {host_data['vulns']}")
        print(f"  Software: {host_data['software']}")
        if host_data['os']:
            print(f"  OS: {host_data['os']}")

    print(f"\n{'='*60}")
    print(f"Findings ({len(findings)})")
    print(f"{'='*60}")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()
