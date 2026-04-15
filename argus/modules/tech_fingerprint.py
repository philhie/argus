"""M07: Wappalyzer-style Technology Fingerprinting.

Detects web technologies from HTTP headers, HTML content, script URLs, and cookies.
No API key required.

Usage: python -m argus.modules.tech_fingerprint example.de
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.tech_fingerprint")

# ---------------------------------------------------------------------------
# Technology signatures
# ---------------------------------------------------------------------------
# Each entry can match via:
#   "header" + "pattern"  — regex matched against that response header
#   "html"                — regex matched against the HTML body
#   "cookie"              — exact cookie name lookup
# Capture group 1, when present, is treated as version string.
# ---------------------------------------------------------------------------

TECH_SIGNATURES: list[dict[str, Any]] = [
    # -- Web servers (header-based) ------------------------------------------
    {"name": "Apache", "cat": "webserver", "header": "Server", "pattern": r"Apache(?:/(\d[\d.]*))?"},
    {"name": "nginx", "cat": "webserver", "header": "Server", "pattern": r"nginx(?:/(\d[\d.]*))?"},
    {"name": "IIS", "cat": "webserver", "header": "Server", "pattern": r"Microsoft-IIS(?:/(\d[\d.]*))?"},
    {"name": "LiteSpeed", "cat": "webserver", "header": "Server", "pattern": r"LiteSpeed(?:/(\d[\d.]*))?"},
    {"name": "Cloudflare", "cat": "cdn", "header": "Server", "pattern": r"cloudflare"},
    {"name": "Varnish", "cat": "cache", "header": "Via", "pattern": r"varnish"},

    # -- Languages / runtimes (header-based) ---------------------------------
    {"name": "PHP", "cat": "language", "header": "X-Powered-By", "pattern": r"PHP(?:/(\d[\d.]*))?"},
    {"name": "ASP.NET", "cat": "framework", "header": "X-Powered-By", "pattern": r"ASP\.NET"},
    {"name": "Express", "cat": "framework", "header": "X-Powered-By", "pattern": r"Express"},

    # -- CMS (HTML-based) ----------------------------------------------------
    {"name": "WordPress", "cat": "cms", "html": r'wp-content|wp-includes|<meta[^>]*generator[^>]*WordPress\s*([\d.]+)?'},
    {"name": "TYPO3", "cat": "cms", "html": r'typo3|<meta[^>]*generator[^>]*TYPO3\s*([\d.]+)?'},
    {"name": "Joomla", "cat": "cms", "html": r'<meta[^>]*generator[^>]*Joomla[!\s]*([\d.]+)?'},
    {"name": "Drupal", "cat": "cms", "html": r'Drupal|drupal\.js'},
    {"name": "Contao", "cat": "cms", "html": r'contao|<meta[^>]*generator[^>]*Contao\s*([\d.]+)?'},
    {"name": "Plone", "cat": "cms", "html": r'plone|portal_css'},
    {"name": "Wix", "cat": "cms", "html": r'wix\.com|X-Wix-'},
    {"name": "Squarespace", "cat": "cms", "html": r'squarespace'},

    # -- E-Commerce ----------------------------------------------------------
    {"name": "Shopware", "cat": "ecommerce", "html": r'shopware|/themes/Frontend/Responsive'},
    {"name": "Magento", "cat": "ecommerce", "html": r'Magento|mage/cookies'},
    {"name": "WooCommerce", "cat": "ecommerce", "html": r'woocommerce|wc-cart'},
    {"name": "Shopify", "cat": "ecommerce", "html": r'cdn\.shopify\.com|Shopify\.theme'},
    {"name": "PrestaShop", "cat": "ecommerce", "html": r'prestashop|PrestaShop'},

    # -- JS libraries / frameworks -------------------------------------------
    {"name": "jQuery", "cat": "js-lib", "html": r'jquery[.-](\d[\d.]+)\.(?:min\.)?js'},
    {"name": "React", "cat": "js-framework", "html": r'react(?:\.production)?\.min\.js|__NEXT_DATA__|_next/static'},
    {"name": "Angular", "cat": "js-framework", "html": r'ng-version="([\d.]+)"|angular(?:\.min)?\.js'},
    {"name": "Vue.js", "cat": "js-framework", "html": r'vue(?:\.runtime)?(?:\.global)?(?:\.min)?\.js|__VUE__'},
    {"name": "Next.js", "cat": "js-framework", "html": r'_next/static|__NEXT_DATA__'},
    {"name": "Nuxt", "cat": "js-framework", "html": r'__NUXT__|_nuxt/'},
    {"name": "Bootstrap", "cat": "css-framework", "html": r'bootstrap(?:\.min)?\.(?:css|js)'},
    {"name": "Tailwind CSS", "cat": "css-framework", "html": r'tailwindcss|tailwind\.min\.css'},

    # -- Cookie-based --------------------------------------------------------
    {"name": "PHP", "cat": "language", "cookie": "PHPSESSID"},
    {"name": "ASP.NET", "cat": "framework", "cookie": "ASP.NET_SessionId"},
    {"name": "Java", "cat": "language", "cookie": "JSESSIONID"},
    {"name": "ColdFusion", "cat": "language", "cookie": "CFID"},
    {"name": "Laravel", "cat": "framework", "cookie": "laravel_session"},

    # -- German-specific / DSGVO consent & analytics -------------------------
    {"name": "Cookiebot", "cat": "consent", "html": r'cookiebot|CookieConsent'},
    {"name": "Usercentrics", "cat": "consent", "html": r'usercentrics'},
    {"name": "Borlabs Cookie", "cat": "consent", "html": r'borlabs-cookie'},
    {"name": "etracker", "cat": "analytics", "html": r'etracker'},
    {"name": "Matomo", "cat": "analytics", "html": r'matomo|piwik'},
    {"name": "Google Analytics", "cat": "analytics", "html": r'google-analytics|googletagmanager|gtag'},
    {"name": "HubSpot", "cat": "marketing", "html": r'hubspot|hs-scripts'},
    {"name": "Google Tag Manager", "cat": "tag-manager", "html": r'googletagmanager\.com/gtm\.js'},
]

# ---------------------------------------------------------------------------
# Known EOL / outdated version thresholds
# If the detected version's major (or major.minor) is below the threshold,
# it is considered outdated.
# ---------------------------------------------------------------------------

EOL_THRESHOLDS: dict[str, tuple[int, ...]] = {
    "WordPress": (6, 0),
    "TYPO3": (11,),
    "Joomla": (4,),
    "Drupal": (10,),
    "PHP": (8, 0),
    "Apache": (2, 4),
    "nginx": (1, 22),
    "IIS": (10,),
    "jQuery": (3, 0),
    "Angular": (14,),
    "Magento": (2, 4),
    "Shopware": (6,),
}


def _parse_version_tuple(version_str: str) -> Optional[tuple[int, ...]]:
    """Parse '8.1.2' into (8, 1, 2). Returns None on failure."""
    parts = version_str.strip().split(".")
    try:
        return tuple(int(p) for p in parts if p)
    except ValueError:
        return None


def _is_outdated(name: str, version: Optional[str]) -> bool:
    """Return True if the detected version is below the EOL threshold."""
    if not version or name not in EOL_THRESHOLDS:
        return False
    parsed = _parse_version_tuple(version)
    if not parsed:
        return False
    threshold = EOL_THRESHOLDS[name]
    # Compare only as many components as the threshold specifies
    return parsed[: len(threshold)] < threshold


# ---------------------------------------------------------------------------
# Core detection
# ---------------------------------------------------------------------------


def detect_technologies(domain: str) -> tuple[list[dict[str, Any]], list[Finding]]:
    """Fetch the domain and detect technologies.

    Returns (technologies, findings).
    """
    technologies: list[dict[str, Any]] = []
    findings: list[Finding] = []
    seen_names: set[str] = set()

    url = f"https://{domain}"
    try:
        resp = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            verify=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ARGUS-Scanner/0.1)"},
        )
    except requests.RequestException as exc:
        logger.debug("Failed to fetch %s: %s", url, exc)
        return technologies, findings

    headers = resp.headers
    body = resp.text
    cookies = {c.name for c in resp.cookies}

    # ---- Match every signature -------------------------------------------
    for sig in TECH_SIGNATURES:
        version: Optional[str] = None

        # Header-based detection
        if "header" in sig:
            header_val = headers.get(sig["header"], "")
            if not header_val:
                continue
            match = re.search(sig["pattern"], header_val, re.IGNORECASE)
            if not match:
                continue
            if match.lastindex and match.lastindex >= 1:
                version = match.group(1)
        # HTML-based detection
        elif "html" in sig:
            match = re.search(sig["html"], body, re.IGNORECASE)
            if not match:
                continue
            if match.lastindex and match.lastindex >= 1:
                version = match.group(1)
        # Cookie-based detection
        elif "cookie" in sig:
            if sig["cookie"] not in cookies:
                continue
        else:
            continue

        name = sig["name"]
        # Avoid duplicates (e.g. PHP detected via header AND cookie)
        if name in seen_names:
            # Update version if we now have one and didn't before
            if version:
                for tech in technologies:
                    if tech["name"] == name and not tech.get("version"):
                        tech["version"] = version
            continue

        seen_names.add(name)
        technologies.append({
            "name": name,
            "version": version,
            "category": sig["cat"],
        })

    # ---- Generate findings -----------------------------------------------

    # TECH-001: Outdated / EOL software
    for tech in technologies:
        if _is_outdated(tech["name"], tech.get("version")):
            findings.append(Finding(
                id="TECH-001",
                module="tech_fingerprint",
                category="infrastructure",
                title=f"Veraltete Software: {tech['name']} {tech['version']}",
                description=(
                    f"Die eingesetzte Version von {tech['name']} ({tech['version']}) "
                    f"ist veraltet und erhält möglicherweise keine Sicherheitsupdates mehr. "
                    f"Angreifer nutzen bekannte Schwachstellen in alten Versionen aktiv aus."
                ),
                severity=Severity.HIGH,
                evidence=f"Erkannt auf {url}: {tech['name']} {tech['version']}",
                nis2_paragraphs=["§30 Abs. 2 Nr. 5"],
                remediation=(
                    f"{tech['name']} auf die aktuelle stabile Version aktualisieren "
                    f"und einen Patch-Management-Prozess etablieren."
                ),
            ))

    # TECH-002: Server header leaks version info
    server_header = headers.get("Server", "")
    if server_header and re.search(r"/\d", server_header):
        findings.append(Finding(
            id="TECH-002",
            module="tech_fingerprint",
            category="infrastructure",
            title=f"Server-Header verrät Version: {server_header}",
            description=(
                "Der Server-Header enthält Versionsinformationen, die einem Angreifer "
                "die gezielte Suche nach bekannten Schwachstellen erleichtern."
            ),
            severity=Severity.LOW,
            evidence=f"Server: {server_header}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 5"],
            remediation="Versionsinformationen aus dem Server-Header entfernen (ServerTokens Prod / server_tokens off).",
        ))

    return technologies, findings


# ---------------------------------------------------------------------------
# Module class
# ---------------------------------------------------------------------------


@register
class TechFingerprintModule(BaseModule):
    name = "tech_fingerprint"
    description = "Technology Fingerprinting"
    phase = 5
    step = 9

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        technologies, findings = detect_technologies(domain)
        context.technologies.extend(technologies)

        logger.info(
            "Detected %d technologies for %s: %s",
            len(technologies),
            domain,
            ", ".join(t["name"] + (f" {t['version']}" if t.get("version") else "") for t in technologies),
        )
        return findings


# ---------------------------------------------------------------------------
# Standalone CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.tech_fingerprint <domain>")
        sys.exit(1)

    target = sys.argv[1]
    if target.startswith("http"):
        # Strip scheme for the function
        target = target.split("://", 1)[1].rstrip("/")

    logging.basicConfig(level=logging.DEBUG)
    techs, fds = detect_technologies(target)

    print(f"\n=== Technologies detected for {target} ===")
    for t in techs:
        ver = t.get("version") or "?"
        print(f"  [{t['category']}] {t['name']} {ver}")

    print(f"\n=== Findings ({len(fds)}) ===")
    for f in fds:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")

    print(f"\n{len(techs)} technologies, {len(fds)} findings")
