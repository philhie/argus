"""M08: Exchange Detection & NTLM Challenge.

The "woah" module — detects Exchange servers, enumerates endpoints,
extracts AD domain and internal hostnames via NTLM challenge.

Usage: python -m argus.modules.exchange mail.true-fruits.com
"""

from __future__ import annotations

import base64
import logging
import struct
from typing import Any, Optional

import warnings

import requests
import urllib3

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.exchange")

EXCHANGE_ENDPOINTS = [
    "/owa",
    "/ecp",
    "/ews/exchange.asmx",
    "/Microsoft-Server-ActiveSync",
    "/mapi",
    "/rpc",
    "/PowerShell",
    "/autodiscover/autodiscover.xml",
    "/oab",
]

# NTLM Type 1 message (minimal, triggers Type 2 response)
NTLM_TYPE1 = base64.b64encode(
    b'\x4e\x54\x4c\x4d\x53\x53\x50\x00'
    b'\x01\x00\x00\x00'
    b'\x07\x82\x08\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00'
).decode()

# Exchange version mapping
EXCHANGE_VERSIONS: dict[str, dict[str, Any]] = {
    "15.2": {
        "name": "Exchange Server 2019",
        "eol_extended": "2025-10-14",
        "eol_esu": "2026-04-14",
        "is_eol": True,
    },
    "15.1": {
        "name": "Exchange Server 2016",
        "eol_extended": "2025-10-14",
        "eol_esu": "2026-04-14",
        "is_eol": True,
    },
    "15.0": {
        "name": "Exchange Server 2013",
        "eol": "2023-04-11",
        "is_eol": True,
    },
    "14.": {
        "name": "Exchange Server 2010",
        "eol": "2020-10-13",
        "is_eol": True,
    },
}


def _decode_ntlm_type2(data: bytes) -> dict[str, str]:
    """Decode NTLM Type 2 challenge to extract AD domain info."""
    result: dict[str, str] = {}

    if len(data) < 56:
        return result

    try:
        target_info_len = struct.unpack('<H', data[40:42])[0]
        target_info_offset = struct.unpack('<I', data[44:48])[0]

        if target_info_offset + target_info_len > len(data):
            return result

        offset = target_info_offset
        while offset < target_info_offset + target_info_len:
            if offset + 4 > len(data):
                break
            av_id = struct.unpack('<H', data[offset:offset + 2])[0]
            av_len = struct.unpack('<H', data[offset + 2:offset + 4])[0]
            av_value = data[offset + 4:offset + 4 + av_len]

            if av_id == 0:  # MsvAvEOL
                break
            elif av_id == 1:  # MsvAvNbComputerName
                result["netbios_computer"] = av_value.decode('utf-16-le')
            elif av_id == 2:  # MsvAvNbDomainName
                result["netbios_domain"] = av_value.decode('utf-16-le')
            elif av_id == 3:  # MsvAvDnsComputerName
                result["dns_computer"] = av_value.decode('utf-16-le')
            elif av_id == 4:  # MsvAvDnsDomainName
                result["dns_domain"] = av_value.decode('utf-16-le')
            elif av_id == 5:  # MsvAvDnsTreeName
                result["dns_tree"] = av_value.decode('utf-16-le')

            offset += 4 + av_len
    except (struct.error, UnicodeDecodeError) as e:
        logger.debug(f"NTLM decode error: {e}")

    return result


def _exchange_get(url: str, **kwargs) -> requests.Response:
    """HTTP GET with SSL verification disabled and warnings suppressed (Exchange only)."""
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("verify", False)
    kwargs.setdefault("allow_redirects", False)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
        return requests.get(url, **kwargs)


def _map_exchange_version(version: str) -> tuple[Optional[str], bool]:
    """Map version string to name and EOL status."""
    for prefix, info in EXCHANGE_VERSIONS.items():
        if version.startswith(prefix):
            return info["name"], info["is_eol"]
    return None, False


def scan_exchange(mail_host: str) -> tuple[dict[str, Any], list[Finding]]:
    """Scan a potential Exchange server. Returns (exchange_info, findings).

    SSL verification is disabled for Exchange servers (self-signed certs are common).
    Warnings are suppressed only within this function scope.
    """
    info: dict[str, Any] = {
        "is_exchange": False,
        "host": mail_host,
        "version": None,
        "version_name": None,
        "is_eol": False,
        "endpoints_exposed": [],
        "auth_methods": {},
        "ntlm_domain": None,
        "ntlm_fqdn": None,
        "ntlm_netbios": None,
        "internal_hostname": None,
    }
    findings: list[Finding] = []
    base_url = f"https://{mail_host}"

    # Check each endpoint
    for endpoint in EXCHANGE_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        try:
            resp = _exchange_get(url)
            if resp.status_code in (200, 301, 302, 401, 403):
                info["is_exchange"] = True
                info["endpoints_exposed"].append(endpoint)

                # Extract auth methods
                www_auth = resp.headers.get("WWW-Authenticate", "")
                methods = []
                if "NTLM" in www_auth:
                    methods.append("NTLM")
                if "Negotiate" in www_auth:
                    methods.append("Negotiate")
                if "Basic" in www_auth:
                    methods.append("Basic")
                info["auth_methods"][endpoint] = methods

                # Extract version from OWA
                owa_version = resp.headers.get("X-OWA-Version")
                if owa_version:
                    info["version"] = owa_version
                    info["version_name"], info["is_eol"] = _map_exchange_version(owa_version)

                # Extract internal hostname
                fe_server = resp.headers.get("X-FEServer")
                if fe_server:
                    info["internal_hostname"] = fe_server

        except requests.RequestException:
            continue

    if not info["is_exchange"]:
        return info, findings

    # --- NTLM Challenge ---
    from argus.config import settings
    ntlm_endpoint = None
    if settings.enable_ntlm:
        for ep, methods in info["auth_methods"].items():
            if "NTLM" in methods:
                ntlm_endpoint = ep
                break

    if ntlm_endpoint:
        try:
            resp = _exchange_get(
                f"{base_url}{ntlm_endpoint}",
                headers={"Authorization": f"NTLM {NTLM_TYPE1}"},
            )
            www_auth = resp.headers.get("WWW-Authenticate", "")
            if "NTLM " in www_auth:
                ntlm_b64 = www_auth.split("NTLM ")[1].split(",")[0].strip()
                ntlm_data = base64.b64decode(ntlm_b64)
                decoded = _decode_ntlm_type2(ntlm_data)
                info["ntlm_domain"] = decoded.get("dns_domain")
                info["ntlm_fqdn"] = decoded.get("dns_computer")
                info["ntlm_netbios"] = decoded.get("netbios_domain")
        except (requests.RequestException, Exception) as e:
            logger.debug(f"NTLM challenge failed: {e}")

    # --- Generate Findings ---

    # EX-001: Exchange EOL
    if info["is_eol"]:
        findings.append(Finding(
            id="EX-001",
            module="exchange",
            category="exchange_exposure",
            title=f"Exchange Server End-of-Life: {info['version_name'] or 'Unbekannte Version'}",
            description=(
                f"Der Exchange Server ({info['version_name'] or info['version']}) "
                f"hat das End-of-Life erreicht und erhält keine Sicherheitsupdates mehr. "
                f"Bekannte Schwachstellen werden nicht mehr gepatcht."
            ),
            severity=Severity.CRITICAL,
            evidence=(
                f"X-OWA-Version: {info['version']} → {info['version_name']} "
                f"(End-of-Life)"
            ),
            nis2_paragraphs=["§30 Abs. 2 Nr. 5", "§30 Abs. 2 Nr. 1"],
            remediation="Migration auf Exchange Online oder Exchange Server 2025 (Subscription Edition).",
        ))

    # EX-002/003: Exposed endpoints
    critical_endpoints = {"/ecp": "EX-003", "/PowerShell": "EX-004"}
    for ep in info["endpoints_exposed"]:
        if ep in critical_endpoints:
            findings.append(Finding(
                id=critical_endpoints[ep],
                module="exchange",
                category="exchange_exposure",
                title=f"Exchange {ep} öffentlich erreichbar",
                description=(
                    f"Der Endpoint {ep} ist ohne VPN oder IP-Beschränkung erreichbar. "
                    f"{'/ecp ist das Admin-Panel.' if ep == '/ecp' else '/PowerShell ermöglicht Remote-Administration.'}"
                ),
                severity=Severity.CRITICAL,
                evidence=f"GET https://{mail_host}{ep} → HTTP erreichbar",
                nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
                remediation=f"Zugriff auf {ep} per Firewall oder Reverse Proxy auf interne IPs beschränken.",
            ))

    if len(info["endpoints_exposed"]) > 5:
        findings.append(Finding(
            id="EX-010",
            module="exchange",
            category="exchange_exposure",
            title=f"{len(info['endpoints_exposed'])} Exchange-Endpoints öffentlich erreichbar",
            severity=Severity.HIGH,
            evidence=f"Exponierte Endpoints: {', '.join(info['endpoints_exposed'])}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation="Alle nicht benötigten Exchange-Endpoints per Reverse Proxy blockieren.",
        ))

    # EX-005: Basic Auth
    for ep, methods in info["auth_methods"].items():
        if "Basic" in methods:
            findings.append(Finding(
                id="EX-005",
                module="exchange",
                category="exchange_exposure",
                title=f"Basic Authentication auf Exchange-Endpoint {ep}",
                description=(
                    "Basic Authentication überträgt Zugangsdaten als Base64-kodierten "
                    "Text. Ohne TLS sind diese im Klartext lesbar. Selbst mit TLS "
                    "erhöht es die Angriffsfläche für Credential-Stuffing."
                ),
                severity=Severity.HIGH,
                evidence=f"WWW-Authenticate auf {ep} enthält 'Basic'",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation="Basic Authentication deaktivieren. Modern Authentication (OAuth) verwenden.",
            ))
            break  # One finding is enough

    # EX-007: AD Domain leaked via NTLM
    if info["ntlm_domain"]:
        findings.append(Finding(
            id="EX-007",
            module="exchange",
            category="exchange_exposure",
            title=f"Active Directory Domain geleakt: {info['ntlm_domain']}",
            description=(
                f"Über eine NTLM-Challenge wurde der interne AD-Domainname "
                f"'{info['ntlm_domain']}' offengelegt. Dies ist normalerweise "
                f"nur innerhalb des Firmennetzwerks sichtbar und verrät die "
                f"interne Netzwerkstruktur."
            ),
            severity=Severity.CRITICAL,
            evidence=(
                f"NTLM Challenge auf https://{mail_host}{ntlm_endpoint} → "
                f"AD Domain: {info['ntlm_domain']}"
                f"{', FQDN: ' + info['ntlm_fqdn'] if info['ntlm_fqdn'] else ''}"
                f"{', NetBIOS: ' + info['ntlm_netbios'] if info['ntlm_netbios'] else ''}"
            ),
            nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 9"],
            remediation="NTLM-Authentifizierung auf Exchange-Endpoints deaktivieren. Auf Kerberos/OAuth umstellen.",
        ))

    # EX-008: Server FQDN leaked
    if info["ntlm_fqdn"]:
        findings.append(Finding(
            id="EX-008",
            module="exchange",
            category="exchange_exposure",
            title=f"Server-FQDN geleakt: {info['ntlm_fqdn']}",
            severity=Severity.HIGH,
            evidence=f"NTLM Challenge → DNS Computer Name: {info['ntlm_fqdn']}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation="NTLM deaktivieren oder Extended Protection aktivieren.",
        ))

    # EX-009: Internal hostname from X-FEServer
    if info["internal_hostname"]:
        findings.append(Finding(
            id="EX-009",
            module="exchange",
            category="exchange_exposure",
            title=f"Interner Hostname geleakt via X-FEServer: {info['internal_hostname']}",
            severity=Severity.MEDIUM,
            evidence=f"X-FEServer: {info['internal_hostname']}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation="X-FEServer Header per Reverse Proxy entfernen.",
        ))

    return info, findings


@register
class ExchangeModule(BaseModule):
    name = "exchange"
    description = "Exchange Detection & NTLM Challenge"
    phase = 3
    step = 3

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        all_findings: list[Finding] = []

        # Try autodiscover and mail subdomains
        candidates = [f"autodiscover.{domain}", f"mail.{domain}"]
        # Also try MX hosts that look like Exchange
        for mx_host in context.mx_hosts:
            mx_lower = mx_host.lower()
            # Skip known cloud providers
            if any(p in mx_lower for p in [
                "google", "outlook.com", "protection.outlook",
                "pphosted", "mimecast", "barracuda",
            ]):
                continue
            candidates.append(mx_host)

        for host in candidates:
            info, findings = scan_exchange(host)
            if info["is_exchange"]:
                all_findings.extend(findings)
                break  # Found Exchange, stop looking

        return all_findings


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.exchange <mail_host>")
        sys.exit(1)

    host = sys.argv[1]
    print(f"Scanning Exchange on {host}...")
    info, findings = scan_exchange(host)

    print(f"\nExchange detected: {info['is_exchange']}")
    if info["is_exchange"]:
        print(f"Version: {info['version_name']} ({info['version']})")
        print(f"Endpoints: {info['endpoints_exposed']}")
        print(f"NTLM Domain: {info['ntlm_domain']}")
        print(f"NTLM FQDN: {info['ntlm_fqdn']}")
        print(f"Internal Host: {info['internal_hostname']}")
        print(f"\nFindings ({len(findings)}):")
        for f in findings:
            print(f"  [{f.severity.value}] {f.id}: {f.title}")
