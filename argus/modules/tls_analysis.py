"""M06: TLS Analysis — protocol versions and cipher strength.

Checks TLS 1.0/1.1/1.3 support and weak cipher suites.
Does NOT duplicate cert_san.py checks (SANs, expiry, self-signed).

Usage: python -m argus.modules.tls_analysis example.com
"""

from __future__ import annotations

import logging
import socket
import ssl

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.tls_analysis")

# Cipher substrings that indicate weakness
WEAK_CIPHER_TOKENS = {"RC4", "DES", "NULL", "EXPORT", "ANON", "MD5"}
SWEET32_TOKENS = {"3DES", "DES-CBC3", "IDEA", "DES-CBC"}


def is_weak_cipher(cipher_name: str) -> bool:
    """Check if a cipher name contains weak algorithm tokens."""
    upper = cipher_name.upper()
    return any(token in upper for token in WEAK_CIPHER_TOKENS)


def is_sweet32_cipher(cipher_name: str) -> bool:
    """Check for 64-bit block cipher (SWEET32 vulnerability)."""
    upper = cipher_name.upper()
    return any(token in upper for token in SWEET32_TOKENS)


def _try_tls_version(
    host: str,
    port: int,
    min_ver: ssl.TLSVersion,
    max_ver: ssl.TLSVersion,
    timeout: int = 5,
) -> tuple[bool, str | None]:
    """Try connecting with a specific TLS version range.

    Returns (success, cipher_name_or_None).
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        ctx.minimum_version = min_ver
        ctx.maximum_version = max_ver
    except (ValueError, ssl.SSLError):
        # Platform may not support setting these versions
        return False, None

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cipher_info = ssock.cipher()
                cipher_name = cipher_info[0] if cipher_info else None
                return True, cipher_name
    except (ssl.SSLError, OSError, ConnectionError, TimeoutError):
        return False, None


def analyze_tls(host: str, port: int = 443) -> list[Finding]:
    """Analyze TLS configuration for a single host."""
    findings: list[Finding] = []
    host_short = host[:30]

    # Test TLS 1.0
    tls10_ok, _ = _try_tls_version(
        host, port, ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1
    )
    if tls10_ok:
        findings.append(Finding(
            id=f"TLS-001-{host_short}",
            module="tls_analysis",
            category="infrastructure",
            title=f"TLS 1.0 aktiviert auf {host}",
            description=(
                f"Der Server {host} unterstützt das veraltete Protokoll TLS 1.0, "
                f"das seit 2020 als unsicher gilt (RFC 8996). Angreifer können bekannte "
                f"Schwachstellen wie POODLE und BEAST ausnutzen."
            ),
            severity=Severity.HIGH,
            evidence=f"TLS-Verbindung mit TLSv1.0 zu {host}:{port} erfolgreich",
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation=(
                "TLS 1.0 auf dem Server deaktivieren. "
                "Nur TLS 1.2 und TLS 1.3 zulassen."
            ),
        ))

    # Test TLS 1.1
    tls11_ok, _ = _try_tls_version(
        host, port, ssl.TLSVersion.TLSv1_1, ssl.TLSVersion.TLSv1_1
    )
    if tls11_ok:
        findings.append(Finding(
            id=f"TLS-002-{host_short}",
            module="tls_analysis",
            category="infrastructure",
            title=f"TLS 1.1 aktiviert auf {host}",
            description=(
                f"Der Server {host} unterstützt TLS 1.1, das seit 2020 als veraltet "
                f"gilt (RFC 8996). Alle modernen Browser haben TLS 1.1 bereits deaktiviert."
            ),
            severity=Severity.MEDIUM,
            evidence=f"TLS-Verbindung mit TLSv1.1 zu {host}:{port} erfolgreich",
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation=(
                "TLS 1.1 auf dem Server deaktivieren. "
                "Nur TLS 1.2 und TLS 1.3 zulassen."
            ),
        ))

    # Test TLS 1.3 support
    tls13_ok, _ = _try_tls_version(
        host, port, ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3
    )
    if not tls13_ok:
        # Verify the host is reachable at all before flagging missing TLS 1.3
        tls12_ok, _ = _try_tls_version(
            host, port, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2
        )
        if tls12_ok:
            findings.append(Finding(
                id=f"TLS-004-{host_short}",
                module="tls_analysis",
                category="infrastructure",
                title=f"Kein TLS 1.3 auf {host}",
                description=(
                    f"Der Server {host} unterstützt nicht das aktuelle Protokoll TLS 1.3, "
                    f"das verbesserte Performance und Sicherheit bietet."
                ),
                severity=Severity.LOW,
                evidence=f"TLS 1.3-Verbindung zu {host}:{port} fehlgeschlagen, TLS 1.2 verfügbar",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation=(
                    "TLS 1.3 auf dem Server aktivieren. "
                    "Bei Apache: SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1. "
                    "Bei Nginx: ssl_protocols TLSv1.2 TLSv1.3;"
                ),
            ))

    # Check negotiated cipher with best available TLS
    best_ok, cipher_name = _try_tls_version(
        host, port, ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.MAXIMUM_SUPPORTED
    )
    if best_ok and cipher_name:
        if is_weak_cipher(cipher_name):
            findings.append(Finding(
                id=f"TLS-003-{host_short}",
                module="tls_analysis",
                category="infrastructure",
                title=f"Schwache Cipher-Suites auf {host}",
                description=(
                    f"Der Server {host} verwendet schwache Verschlüsselungsalgorithmen: "
                    f"{cipher_name}. Diese bieten keinen ausreichenden Schutz."
                ),
                severity=Severity.HIGH,
                evidence=f"Ausgehandelte Cipher: {cipher_name} auf {host}:{port}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation=(
                    "Schwache Cipher-Suites in der TLS-Konfiguration deaktivieren. "
                    "Mozilla SSL Configuration Generator verwenden: "
                    "https://ssl-config.mozilla.org/"
                ),
            ))

        if is_sweet32_cipher(cipher_name):
            findings.append(Finding(
                id=f"TLS-005-{host_short}",
                module="tls_analysis",
                category="infrastructure",
                title=f"SWEET32/BEAST-anfällige Cipher auf {host}",
                description=(
                    f"Der Server {host} verwendet Cipher-Suites, die für SWEET32- oder "
                    f"BEAST-Angriffe anfällig sind: {cipher_name}. "
                    f"64-Bit-Blockchiffren ermöglichen praktische Angriffe."
                ),
                severity=Severity.HIGH,
                evidence=f"Ausgehandelte Cipher: {cipher_name} auf {host}:{port}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation=(
                    "3DES und andere 64-Bit-Blockchiffren deaktivieren. "
                    "Nur AES-basierte Cipher-Suites verwenden."
                ),
            ))

    return findings


def _build_host_list(domain: str, context: ScanContext) -> list[str]:
    """Build deduplicated list of hosts to check."""
    hosts = [domain]
    for mx in context.mx_hosts[:3]:
        if mx not in hosts:
            hosts.append(mx)
    for sub in context.subdomains[:5]:
        if sub not in hosts:
            hosts.append(sub)
    return hosts


def scan_tls(domain: str, context: ScanContext) -> list[Finding]:
    """Run TLS analysis across all relevant hosts."""
    findings: list[Finding] = []
    hosts = _build_host_list(domain, context)

    for host in hosts:
        try:
            host_findings = analyze_tls(host)
            findings.extend(host_findings)
        except Exception as e:
            logger.debug(f"TLS-Analyse für {host} fehlgeschlagen: {e}")
            continue

    return findings


@register
class TlsAnalysisModule(BaseModule):
    name = "tls_analysis"
    description = "TLS versions, cipher suites, weak algorithms"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_tls(domain, context)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"

    ctx = ScanContext(domain=target)
    results = scan_tls(target, ctx)
    print(f"\n{len(results)} Findings:")
    for f in results:
        print(f"  [{f.severity.value}] {f.title}")
        print(f"    {f.evidence}")
