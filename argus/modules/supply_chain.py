"""M14: Third-Party Supply Chain Mapping.

Usage: python -m argus.modules.supply_chain example.com
"""

from __future__ import annotations

import logging
import re

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.supply_chain")

KNOWN_SERVICES: dict[str, list[str]] = {
    "Google Analytics": ["google-analytics.com", "googletagmanager.com", "gtag"],
    "Google Tag Manager": ["googletagmanager.com/gtm.js"],
    "HubSpot": ["js.hs-scripts.com", "js.hubspot.com"],
    "Hotjar": ["static.hotjar.com"],
    "Matomo": ["matomo", "piwik"],
    "Facebook Pixel": ["connect.facebook.net", "fbevents.js"],
    "LinkedIn Insight": ["snap.licdn.com"],
    "Cookiebot": ["consent.cookiebot.com"],
    "Usercentrics": ["usercentrics.eu"],
    "Cloudflare": ["cdnjs.cloudflare.com", "cdn.cloudflare.com"],
    "jQuery CDN": ["code.jquery.com"],
    "Bootstrap CDN": ["cdn.jsdelivr.net/npm/bootstrap", "stackpath.bootstrapcdn.com"],
    "Font Awesome": ["fontawesome", "fa-"],
    "Google Fonts": ["fonts.googleapis.com", "fonts.gstatic.com"],
    "Stripe": ["js.stripe.com"],
    "PayPal": ["paypal.com/sdk"],
    "Intercom": ["widget.intercom.io"],
    "Zendesk": ["static.zdassets.com"],
    "Drift": ["js.driftt.com"],
    "Salesforce": ["salesforce.com", "pardot.com"],
    "Sentry": ["browser.sentry-cdn.com", "sentry.io"],
    "New Relic": ["js-agent.newrelic.com"],
}

# Categorize services
SERVICE_CATEGORIES: dict[str, str] = {
    "Google Analytics": "Analytics",
    "Google Tag Manager": "Tag Management",
    "HubSpot": "Marketing",
    "Hotjar": "Analytics",
    "Matomo": "Analytics",
    "Facebook Pixel": "Tracking",
    "LinkedIn Insight": "Tracking",
    "Cookiebot": "Consent Management",
    "Usercentrics": "Consent Management",
    "Cloudflare": "CDN",
    "jQuery CDN": "CDN",
    "Bootstrap CDN": "CDN",
    "Font Awesome": "CDN",
    "Google Fonts": "CDN",
    "Stripe": "Payment",
    "PayPal": "Payment",
    "Intercom": "Support",
    "Zendesk": "Support",
    "Drift": "Support",
    "Salesforce": "CRM",
    "Sentry": "Monitoring",
    "New Relic": "Monitoring",
}


def check_supply_chain(base_url: str) -> tuple[list[Finding], list[dict[str, str]]]:
    """Map third-party services from HTML sources. Returns findings and entries."""
    findings: list[Finding] = []
    entries: list[dict[str, str]] = []

    try:
        resp = requests.get(base_url, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return findings, entries
    except requests.RequestException:
        return findings, entries

    html = resp.text

    # Extract external resource URLs
    script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    link_preconnects = re.findall(
        r'<link[^>]+rel=["\']preconnect["\'][^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE
    )
    iframe_srcs = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)

    all_urls = script_srcs + link_preconnects + iframe_srcs

    # Match against known services
    identified: set[str] = set()
    for url in all_urls:
        url_lower = url.lower()
        for service, patterns in KNOWN_SERVICES.items():
            if service in identified:
                continue
            for pattern in patterns:
                if pattern in url_lower:
                    identified.add(service)
                    entries.append({
                        "service": service,
                        "category": SERVICE_CATEGORIES.get(service, "Other"),
                        "url": url,
                    })
                    break

    # SC-001: Too many third-party services
    if len(identified) > 10:
        findings.append(Finding(
            id="SC-001",
            module="supply_chain",
            category="supply_chain",
            title=f"{len(identified)} Drittanbieter-Dienste eingebunden",
            description=(
                f"Die Website bindet {len(identified)} externe Dienste ein. "
                f"Jeder Drittanbieter erh\u00f6ht die Angriffsfl\u00e4che und das "
                f"Risiko von Supply-Chain-Angriffen (z.B. Magecart-Angriffe)."
            ),
            severity=Severity.MEDIUM,
            evidence=(
                f"Erkannte Dienste: {', '.join(sorted(identified))}"
            ),
            nis2_paragraphs=["\u00a730 Abs. 2 Nr. 4"],
            remediation=(
                "Drittanbieter-Dienste regelm\u00e4\u00dfig \u00fcberpr\u00fcfen und nicht ben\u00f6tigte "
                "entfernen. Subresource Integrity (SRI) f\u00fcr externe Scripts einsetzen. "
                "Content Security Policy (CSP) implementieren."
            ),
        ))

    # SC-002: External scripts without Subresource Integrity (SRI)
    # Find script tags with external src but no integrity attribute
    script_tags = re.findall(r'<script[^>]*>', html, re.IGNORECASE)
    scripts_without_sri = 0
    external_scripts_total = 0

    for tag in script_tags:
        src_match = re.search(r'src=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if not src_match:
            continue
        src = src_match.group(1)
        # Only check external scripts (not same-origin)
        if src.startswith("http://") or src.startswith("https://") or src.startswith("//"):
            external_scripts_total += 1
            if "integrity=" not in tag.lower():
                scripts_without_sri += 1

    if scripts_without_sri > 0:
        findings.append(Finding(
            id="SC-002",
            module="supply_chain",
            category="supply_chain",
            title="Externe Scripts ohne Subresource Integrity",
            description=(
                f"{scripts_without_sri} von {external_scripts_total} externen Scripts "
                f"werden ohne Subresource Integrity (SRI) geladen. "
                f"Ein kompromittierter CDN-Server k\u00f6nnte manipulierten Code ausliefern."
            ),
            severity=Severity.MEDIUM,
            evidence=(
                f"{scripts_without_sri}/{external_scripts_total} externe "
                f"<script>-Tags ohne integrity-Attribut"
            ),
            nis2_paragraphs=["\u00a730 Abs. 2 Nr. 4"],
            remediation=(
                "Subresource Integrity (SRI) f\u00fcr alle externen Scripts hinzuf\u00fcgen: "
                '<script src="..." integrity="sha384-..." crossorigin="anonymous">. '
                "SRI-Hashes k\u00f6nnen mit srihash.org generiert werden."
            ),
        ))

    return findings, entries


@register
class SupplyChainModule(BaseModule):
    name = "supply_chain"
    description = "Third-Party Supply Chain Mapping"
    phase = 5
    step = 9

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        findings, entries = check_supply_chain(f"https://{domain}")
        context.supply_chain_entries = entries
        return findings


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.supply_chain <domain>")
        sys.exit(1)

    target = sys.argv[1]
    if not target.startswith("http"):
        target = f"https://{target}"
    print(f"Mapping supply chain for {target}...")
    findings, entries = check_supply_chain(target)
    if entries:
        print(f"\nIdentified {len(entries)} third-party services:")
        for e in entries:
            print(f"  [{e['category']}] {e['service']}: {e['url'][:80]}")
    for f in findings:
        print(f"\n  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
