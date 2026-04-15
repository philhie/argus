"""M05: HTTP Security Headers Check.

Usage: python -m argus.modules.http_headers https://true-fruits.com
"""

from __future__ import annotations

import logging
import re

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.http_headers")

# Headers that SHOULD be present
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "id": "HDR-001",
        "severity": Severity.MEDIUM,
        "title": "Strict-Transport-Security (HSTS) Header fehlt",
        "desc": (
            "Ohne HSTS können Benutzer über unverschlüsselte HTTP-Verbindungen "
            "auf die Website zugreifen. Ein Angreifer kann den Traffic "
            "abfangen (Man-in-the-Middle)."
        ),
        "remediation": "HSTS-Header setzen: Strict-Transport-Security: max-age=31536000; includeSubDomains",
        "check": lambda v: bool(re.search(r'max-age=(\d+)', v)) and int(re.search(r'max-age=(\d+)', v).group(1)) >= 31536000,
        "weak_title": "HSTS max-age zu kurz (< 1 Jahr)",
        "weak_severity": Severity.LOW,
    },
    "Content-Security-Policy": {
        "id": "HDR-002",
        "severity": Severity.MEDIUM,
        "title": "Content-Security-Policy (CSP) Header fehlt",
        "desc": (
            "Ohne CSP können eingeschleuste Scripts (XSS) beliebigen Code "
            "im Browser des Benutzers ausführen."
        ),
        "remediation": "CSP-Header mit restriktiver Policy setzen. Mindestens: default-src 'self'",
        "check": lambda v: "unsafe-inline" not in v and "unsafe-eval" not in v,
        "weak_title": "CSP enthält 'unsafe-inline' oder 'unsafe-eval'",
        "weak_severity": Severity.LOW,
    },
    "X-Content-Type-Options": {
        "id": "HDR-003",
        "severity": Severity.LOW,
        "title": "X-Content-Type-Options Header fehlt",
        "desc": "Ohne 'nosniff' kann der Browser MIME-Types raten, was zu Script-Injection führen kann.",
        "remediation": "Header setzen: X-Content-Type-Options: nosniff",
    },
    "X-Frame-Options": {
        "id": "HDR-004",
        "severity": Severity.LOW,
        "title": "X-Frame-Options Header fehlt",
        "desc": "Ohne X-Frame-Options kann die Seite in fremden iframes eingebettet werden (Clickjacking).",
        "remediation": "Header setzen: X-Frame-Options: DENY oder SAMEORIGIN",
    },
    "Permissions-Policy": {
        "id": "HDR-005",
        "severity": Severity.LOW,
        "title": "Permissions-Policy Header fehlt",
        "desc": "Ohne Permissions-Policy können eingebettete Inhalte auf Kamera, Mikrofon und Standort zugreifen.",
        "remediation": "Permissions-Policy Header mit restriktiven Werten setzen.",
    },
    "Referrer-Policy": {
        "id": "HDR-006",
        "severity": Severity.LOW,
        "title": "Referrer-Policy Header fehlt",
        "desc": "Ohne Referrer-Policy werden vollständige URLs an Drittseiten übermittelt.",
        "remediation": "Header setzen: Referrer-Policy: strict-origin-when-cross-origin",
    },
}

# Headers that SHOULD NOT be present (information disclosure)
LEAKY_HEADERS = {
    "X-Powered-By": "HDR-LEAK-001",
    "Server": "HDR-LEAK-002",
    "X-AspNet-Version": "HDR-LEAK-003",
    "X-AspNetMvc-Version": "HDR-LEAK-004",
}


def check_headers(url: str) -> list[Finding]:
    """Check security headers for a URL. Returns findings."""
    findings: list[Finding] = []

    try:
        resp = requests.get(url, timeout=10, allow_redirects=True, verify=True)
        headers = resp.headers
    except requests.RequestException as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return findings

    # Check required security headers
    for header_name, config in SECURITY_HEADERS.items():
        value = headers.get(header_name)
        if value is None:
            findings.append(Finding(
                id=config["id"],
                module="http_headers",
                category="web_application",
                title=config["title"],
                description=config["desc"],
                severity=config["severity"],
                evidence=f"GET {url} → '{header_name}' Header nicht vorhanden",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                remediation=config["remediation"],
            ))
        elif "check" in config:
            try:
                if not config["check"](value):
                    findings.append(Finding(
                        id=config["id"],
                        module="http_headers",
                        category="web_application",
                        title=config.get("weak_title", config["title"]),
                        severity=config.get("weak_severity", Severity.LOW),
                        evidence=f"{header_name}: {value}",
                        nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                        remediation=config["remediation"],
                    ))
            except Exception:
                pass

    # Check leaky headers
    for header_name, finding_id in LEAKY_HEADERS.items():
        value = headers.get(header_name)
        if value:
            # Skip generic "Server" values that don't reveal version
            if header_name == "Server" and value.lower() in ("cloudflare", "nginx", "apache"):
                continue
            findings.append(Finding(
                id=finding_id,
                module="http_headers",
                category="web_application",
                title=f"'{header_name}' Header exponiert Serverinformationen",
                description=(
                    f"Der Header '{header_name}: {value}' verrät Details über die "
                    f"eingesetzte Servertechnologie. Diese Information erleichtert "
                    f"gezielte Angriffe."
                ),
                severity=Severity.LOW,
                evidence=f"{header_name}: {value}",
                nis2_paragraphs=[],
                remediation=f"'{header_name}' Header in der Serverkonfiguration entfernen.",
            ))

    # Check cookies (use resp.cookies to avoid comma-splitting issues with Expires dates)
    for cookie in resp.cookies:
        cookie_attrs = resp.headers.get("Set-Cookie", "")
        if not cookie.secure:
            findings.append(Finding(
                id="HDR-COOKIE-001",
                module="http_headers",
                category="web_application",
                title=f"Cookie '{cookie.name}' ohne Secure-Flag",
                severity=Severity.MEDIUM,
                evidence=f"Cookie '{cookie.name}' wird ohne Secure-Flag gesetzt",
                nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
                remediation="Secure-Flag für alle Cookies setzen.",
            ))
            break  # One cookie finding is enough

    return findings


@register
class HttpHeadersModule(BaseModule):
    name = "http_headers"
    description = "HTTP Security Headers Check"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        url = f"https://{domain}"
        findings = check_headers(url)
        if not context.live_urls:
            context.live_urls.append(url)
        return findings


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.http_headers <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = f"https://{url}"
    print(f"Checking headers for {url}...")
    findings = check_headers(url)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
