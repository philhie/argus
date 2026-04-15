"""M24: CORS Misconfiguration Testing.

Usage: python -m argus.modules.cors https://true-fruits.com
"""

from __future__ import annotations

import logging

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.cors")


def check_cors(url: str) -> list[Finding]:
    """Check for CORS misconfigurations. Returns findings."""
    findings: list[Finding] = []

    # Extract domain for subdomain test
    try:
        domain = url.split("//")[1].split("/")[0]
    except IndexError:
        return findings

    test_origins = [
        "https://evil.com",
        "https://attacker.com",
        f"https://sub.{domain}",
        "null",
    ]

    for origin in test_origins:
        try:
            resp = requests.get(
                url,
                headers={"Origin": origin},
                timeout=10,
                allow_redirects=True,
            )
            acao = resp.headers.get("Access-Control-Allow-Origin", "")
            acac = resp.headers.get("Access-Control-Allow-Credentials", "")

            if acao == "*":
                findings.append(Finding(
                    id="CORS-001",
                    module="cors",
                    category="web_application",
                    title="Wildcard CORS Policy (Access-Control-Allow-Origin: *)",
                    description=(
                        "Der Server erlaubt Cross-Origin-Requests von jeder beliebigen "
                        "Website. In Kombination mit sensitiven API-Endpoints können "
                        "Angreifer Daten aus dem Browser des Benutzers stehlen."
                    ),
                    severity=Severity.HIGH,
                    evidence=f"GET {url} mit Origin: {origin} → Access-Control-Allow-Origin: *",
                    nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                    remediation="CORS-Policy auf spezifische, autorisierte Domains beschränken.",
                ))
                return findings  # Wildcard found, no need to test more

            if acao == origin and origin not in ("null", f"https://sub.{domain}"):
                severity = Severity.CRITICAL if acac.lower() == "true" else Severity.HIGH
                findings.append(Finding(
                    id="CORS-002",
                    module="cors",
                    category="web_application",
                    title="Origin-Reflection CORS — beliebige Websites können API-Requests machen",
                    description=(
                        f"Der Server reflektiert den Origin-Header '{origin}' in der "
                        f"CORS-Antwort. Jede Website kann Cross-Origin-Requests stellen. "
                        f"{'Mit Allow-Credentials können authentifizierte Requests gemacht werden.' if acac.lower() == 'true' else ''}"
                    ),
                    severity=severity,
                    evidence=(
                        f"GET {url} mit Origin: {origin} → "
                        f"Access-Control-Allow-Origin: {acao}, "
                        f"Access-Control-Allow-Credentials: {acac}"
                    ),
                    nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                    remediation="Origin-Reflection abschalten. Nur explizit erlaubte Domains zurückgeben.",
                ))
                return findings  # Reflection found

            if acao == "null":
                findings.append(Finding(
                    id="CORS-003",
                    module="cors",
                    category="web_application",
                    title="Null-Origin in CORS erlaubt",
                    description=(
                        "Der Server erlaubt den 'null' Origin. Sandboxed iframes und "
                        "lokale Dateien senden 'null' als Origin — ein Angreifer kann "
                        "dies ausnutzen."
                    ),
                    severity=Severity.MEDIUM,
                    evidence=f"Access-Control-Allow-Origin: null",
                    nis2_paragraphs=["§30 Abs. 2 Nr. 1"],
                    remediation="'null' Origin in CORS-Konfiguration nicht akzeptieren.",
                ))
                return findings

        except requests.RequestException:
            continue

    return findings


@register
class CorsModule(BaseModule):
    name = "cors"
    description = "CORS Misconfiguration Testing"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_cors(f"https://{domain}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.cors <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = f"https://{url}"
    print(f"Checking CORS for {url}...")
    findings = check_cors(url)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
