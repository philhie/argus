"""M25: Certificate SAN (Subject Alternative Name) Analysis.

Extracts internal hostnames, private IPs, and unknown subdomains from TLS certificates.

Usage: python -m argus.modules.cert_san true-fruits.com
"""

from __future__ import annotations

import logging
import socket
import ssl
from datetime import datetime, timezone
from typing import Any

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.cert_san")

INTERNAL_INDICATORS = [
    ".local", ".internal", ".corp", ".lan", ".intra",
    ".home", ".private", ".ad.", ".domain",
]

PRIVATE_IP_PREFIXES = [
    "192.168.", "10.", "172.16.", "172.17.", "172.18.",
    "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
    "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
    "172.29.", "172.30.", "172.31.",
]


def analyze_certificate(hostname: str, port: int = 443) -> tuple[dict[str, Any], list[Finding]]:
    """Analyze TLS certificate for a hostname. Returns (cert_info, findings)."""
    info: dict[str, Any] = {
        "hostname": hostname,
        "sans": [],
        "internal_names": [],
        "private_ips": [],
        "issuer": None,
        "subject": None,
        "valid_from": None,
        "valid_to": None,
        "days_until_expiry": None,
        "is_self_signed": False,
        "is_wildcard": False,
    }
    findings: list[Finding] = []

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=False)
                if cert is None:
                    # Try binary form
                    der = ssock.getpeercert(binary_form=True)
                    if der is None:
                        return info, findings
                    # We can't parse DER without cryptography, fall through
                    return info, findings

                # Extract SANs
                for san_type, san_value in cert.get("subjectAltName", []):
                    if san_type == "DNS":
                        info["sans"].append(san_value)
                        # Check for internal names
                        lower = san_value.lower()
                        if any(ind in lower for ind in INTERNAL_INDICATORS):
                            info["internal_names"].append(san_value)
                        if san_value.startswith("*."):
                            info["is_wildcard"] = True
                    elif san_type == "IP Address":
                        info["sans"].append(san_value)
                        if any(san_value.startswith(p) for p in PRIVATE_IP_PREFIXES):
                            info["private_ips"].append(san_value)

                # Extract issuer/subject
                subject_parts = dict(x[0] for x in cert.get("subject", ()))
                issuer_parts = dict(x[0] for x in cert.get("issuer", ()))
                info["subject"] = subject_parts.get("commonName")
                info["issuer"] = issuer_parts.get("organizationName") or issuer_parts.get("commonName")

                # Check self-signed
                if subject_parts == issuer_parts:
                    info["is_self_signed"] = True

                # Check validity
                not_after = cert.get("notAfter")
                not_before = cert.get("notBefore")
                if not_after:
                    # Format: 'Mar 15 12:00:00 2025 GMT'
                    try:
                        expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        expiry = expiry.replace(tzinfo=timezone.utc)
                        info["valid_to"] = expiry.isoformat()
                        info["days_until_expiry"] = (expiry - datetime.now(timezone.utc)).days
                    except ValueError:
                        pass
                if not_before:
                    try:
                        valid_from = datetime.strptime(not_before, "%b %d %H:%M:%S %Y %Z")
                        info["valid_from"] = valid_from.replace(tzinfo=timezone.utc).isoformat()
                    except ValueError:
                        pass

    except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
        logger.debug(f"TLS connection to {hostname}:{port} failed: {e}")
        return info, findings
    except Exception as e:
        logger.debug(f"Certificate analysis failed for {hostname}: {e}")
        return info, findings

    # --- Generate Findings ---

    # Use hostname prefix to avoid duplicate IDs across multiple hosts
    host_short = hostname.split(".")[0][:8]

    if info["internal_names"]:
        names = ", ".join(info["internal_names"])
        findings.append(Finding(
            id=f"CERT-001-{host_short}",
            module="cert_san",
            category="infrastructure",
            title=f"Interne Hostnamen in TLS-Zertifikat geleakt",
            description=(
                f"Das TLS-Zertifikat enthält interne Hostnamen in den "
                f"Subject Alternative Names: {names}. Diese verraten die "
                f"interne Netzwerkstruktur und AD-Namenskonventionen."
            ),
            severity=Severity.HIGH,
            evidence=f"TLS Certificate SANs für {hostname} enthalten: {names}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation="Zertifikat ohne interne Hostnamen neu ausstellen. Nur öffentliche Domains in SANs aufnehmen.",
        ))

    if info["private_ips"]:
        ips = ", ".join(info["private_ips"])
        findings.append(Finding(
            id=f"CERT-002-{host_short}",
            module="cert_san",
            category="infrastructure",
            title="Private IP-Adressen in TLS-Zertifikat geleakt",
            severity=Severity.HIGH,
            evidence=f"TLS Certificate SANs für {hostname} enthalten private IPs: {ips}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation="Zertifikat ohne private IP-Adressen neu ausstellen.",
        ))

    if info["is_self_signed"]:
        findings.append(Finding(
            id=f"CERT-004-{host_short}",
            module="cert_san",
            category="infrastructure",
            title="Self-Signed Zertifikat auf Production-Server",
            severity=Severity.MEDIUM,
            evidence=f"Zertifikat für {hostname}: Subject == Issuer (self-signed)",
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation="Zertifikat von einer vertrauenswürdigen CA ausstellen lassen (z.B. Let's Encrypt).",
        ))

    if info["days_until_expiry"] is not None and info["days_until_expiry"] < 30:
        severity = Severity.HIGH if info["days_until_expiry"] < 7 else Severity.MEDIUM
        findings.append(Finding(
            id=f"CERT-005-{host_short}",
            module="cert_san",
            category="infrastructure",
            title=f"TLS-Zertifikat läuft in {info['days_until_expiry']} Tagen ab",
            severity=severity,
            evidence=f"Zertifikat für {hostname} gültig bis: {info['valid_to']}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 3"],
            remediation="Zertifikat vor Ablauf erneuern. Auto-Renewal einrichten.",
        ))

    return info, findings


@register
class CertSanModule(BaseModule):
    name = "cert_san"
    description = "Certificate SAN Analysis"
    phase = 3
    step = 3

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        all_findings: list[Finding] = []

        # Check main domain
        _, findings = analyze_certificate(domain)
        all_findings.extend(findings)

        # Check MX hosts
        for mx_host in context.mx_hosts[:3]:
            _, findings = analyze_certificate(mx_host)
            all_findings.extend(findings)

        return all_findings


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.cert_san <hostname>")
        sys.exit(1)

    host = sys.argv[1]
    print(f"Analyzing certificate for {host}...")
    info, findings = analyze_certificate(host)

    print(f"\nSANs: {info['sans']}")
    print(f"Internal names: {info['internal_names']}")
    print(f"Private IPs: {info['private_ips']}")
    print(f"Issuer: {info['issuer']}")
    print(f"Self-signed: {info['is_self_signed']}")
    print(f"Expires in: {info['days_until_expiry']} days")
    print(f"\nFindings ({len(findings)}):")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
