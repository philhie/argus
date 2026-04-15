"""M31: Subdomain Takeover Detection.

Checks discovered subdomains for dangling CNAME records that could allow
subdomain takeover via unclaimed cloud service endpoints.

Usage: python -m argus.modules.subdomain_takeover example.com
"""

from __future__ import annotations

import logging

import dns.resolver
import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.subdomain_takeover")

TAKEOVER_FINGERPRINTS = {
    "github.io": {
        "service": "GitHub Pages",
        "fingerprint": "There isn't a GitHub Pages site here",
    },
    "herokuapp.com": {
        "service": "Heroku",
        "fingerprint": "No such app",
    },
    "azurewebsites.net": {
        "service": "Azure Web Apps",
        "fingerprint": "404 Web Site not found",
    },
    "cloudapp.net": {
        "service": "Azure",
        "fingerprint": "",
    },
    "s3.amazonaws.com": {
        "service": "AWS S3",
        "fingerprint": "NoSuchBucket",
    },
    "elasticbeanstalk.com": {
        "service": "AWS Elastic Beanstalk",
        "fingerprint": "",
    },
    "shopify.com": {
        "service": "Shopify",
        "fingerprint": "Sorry, this shop is currently unavailable",
    },
    "ghost.io": {
        "service": "Ghost",
        "fingerprint": "Domain is not configured",
    },
    "pantheonsite.io": {
        "service": "Pantheon",
        "fingerprint": "404 error unknown site",
    },
    "zendesk.com": {
        "service": "Zendesk",
        "fingerprint": "Help Center Closed",
    },
    "surge.sh": {
        "service": "Surge.sh",
        "fingerprint": "project not found",
    },
    "feedpress.me": {
        "service": "FeedPress",
        "fingerprint": "The feed has not been found",
    },
    "freshdesk.com": {
        "service": "Freshdesk",
        "fingerprint": "There is no helpdesk here",
    },
    "tumblr.com": {
        "service": "Tumblr",
        "fingerprint": "There's nothing here",
    },
    "wordpress.com": {
        "service": "WordPress.com",
        "fingerprint": "Do you want to register",
    },
}


def _resolve_cname(subdomain: str) -> str | None:
    """Resolve CNAME for a subdomain. Returns target or None."""
    try:
        answers = dns.resolver.resolve(subdomain, "CNAME")
        for rdata in answers:
            return str(rdata.target).rstrip(".")
        return None
    except Exception:
        return None


def _cname_target_resolves(cname_target: str) -> bool:
    """Check whether the CNAME target domain resolves (not NXDOMAIN)."""
    try:
        dns.resolver.resolve(cname_target, "A")
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        # Other errors (timeout, no answer) — assume it exists
        return True


def _match_fingerprint(cname_target: str) -> dict | None:
    """Check if a CNAME target matches a known vulnerable service."""
    cname_lower = cname_target.lower()
    for suffix, info in TAKEOVER_FINGERPRINTS.items():
        if cname_lower.endswith(suffix):
            return info
    return None


def _http_fingerprint_check(subdomain: str, fingerprint: str) -> bool:
    """Try HTTP GET and check if fingerprint text appears in the response."""
    if not fingerprint:
        return False
    for scheme in ("https", "http"):
        try:
            resp = requests.get(
                f"{scheme}://{subdomain}",
                timeout=10,
                allow_redirects=True,
                verify=False,  # noqa: S501 — dangling domains often have bad certs
            )
            if fingerprint in resp.text:
                return True
        except Exception:
            continue
    return False


@register
class SubdomainTakeoverModule(BaseModule):
    name = "subdomain_takeover"
    description = "Subdomain Takeover Detection"
    phase = 3
    step = 5

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        findings: list[Finding] = []

        if not context.subdomains:
            logger.info("No subdomains available, skipping takeover check")
            return findings

        logger.info(
            "Checking %d subdomains for takeover risk", len(context.subdomains)
        )

        for subdomain in context.subdomains:
            try:
                self._check_subdomain(subdomain, findings)
            except Exception:
                logger.debug("Error checking %s, skipping", subdomain, exc_info=True)

        logger.info(
            "Subdomain takeover check complete: %d findings", len(findings)
        )
        return findings

    def _check_subdomain(
        self, subdomain: str, findings: list[Finding]
    ) -> None:
        cname_target = _resolve_cname(subdomain)
        if cname_target is None:
            return

        logger.debug("%s CNAME → %s", subdomain, cname_target)

        # Check if CNAME target resolves at all
        if not _cname_target_resolves(cname_target):
            findings.append(Finding(
                id="TAKEOVER-002",
                module="subdomain_takeover",
                category="infrastructure",
                title=(
                    f"CNAME zeigt auf nicht-existierende Domain: "
                    f"{subdomain} → {cname_target}"
                ),
                description=(
                    f"Der Subdomain {subdomain} hat einen CNAME-Record auf "
                    f"{cname_target}, aber diese Domain existiert nicht (NXDOMAIN). "
                    f"Ein Angreifer kann die Ziel-Domain registrieren und den "
                    f"Subdomain vollständig übernehmen."
                ),
                severity=Severity.CRITICAL,
                evidence=f"dig CNAME {subdomain} → {cname_target} (NXDOMAIN)",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 5"],
                remediation=(
                    f"Den verwaisten CNAME-Record für {subdomain} sofort entfernen. "
                    f"Alle DNS-Records regelmäßig auf verwaiste Einträge prüfen."
                ),
            ))
            return

        # Check against known vulnerable services
        service_info = _match_fingerprint(cname_target)
        if service_info is None:
            return

        service = service_info["service"]
        fingerprint = service_info["fingerprint"]

        # Try HTTP fingerprint confirmation
        if fingerprint and _http_fingerprint_check(subdomain, fingerprint):
            findings.append(Finding(
                id="TAKEOVER-001",
                module="subdomain_takeover",
                category="infrastructure",
                title=f"Subdomain-Takeover möglich: {subdomain} → {service}",
                description=(
                    f"Der Subdomain {subdomain} hat einen CNAME auf {cname_target} "
                    f"({service}), aber der zugehörige Dienst ist nicht konfiguriert. "
                    f"Die charakteristische Fehlermeldung wurde bestätigt. Ein Angreifer "
                    f"kann den Dienst beanspruchen und beliebige Inhalte unter "
                    f"diesem Subdomain bereitstellen."
                ),
                severity=Severity.CRITICAL,
                evidence=(
                    f"CNAME: {subdomain} → {cname_target}\n"
                    f"HTTP-Antwort enthält: \"{fingerprint}\""
                ),
                nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 5"],
                remediation=(
                    f"Den CNAME-Record für {subdomain} entfernen oder den {service}-"
                    f"Dienst korrekt konfigurieren und den Hostnamen beanspruchen."
                ),
            ))
        else:
            findings.append(Finding(
                id="TAKEOVER-003",
                module="subdomain_takeover",
                category="infrastructure",
                title=f"Potentieller Subdomain-Takeover: {subdomain} → {service}",
                description=(
                    f"Der Subdomain {subdomain} hat einen CNAME auf {cname_target} "
                    f"({service}). Eine automatische Bestätigung war nicht möglich, "
                    f"aber der Dienst könnte nicht beansprucht sein. "
                    f"Manuelle Überprüfung empfohlen."
                ),
                severity=Severity.HIGH,
                evidence=f"CNAME: {subdomain} → {cname_target} ({service})",
                nis2_paragraphs=["§30 Abs. 2 Nr. 1", "§30 Abs. 2 Nr. 5"],
                remediation=(
                    f"Prüfen, ob der {service}-Dienst für {subdomain} korrekt "
                    f"konfiguriert ist. Falls nicht benötigt, den CNAME-Record entfernen."
                ),
            ))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.subdomain_takeover <domain>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Checking subdomains of {target} for takeover risk...")

    # Quick standalone test: resolve common subdomains
    test_prefixes = [
        "www", "mail", "app", "blog", "shop", "dev", "staging",
        "test", "api", "cdn", "status", "docs", "support",
    ]
    test_subdomains = [f"{prefix}.{target}" for prefix in test_prefixes]

    found_cnames = 0
    for sub in test_subdomains:
        cname = _resolve_cname(sub)
        if cname is None:
            continue
        found_cnames += 1
        print(f"\n  {sub} CNAME → {cname}")

        if not _cname_target_resolves(cname):
            print("    !! NXDOMAIN — takeover risk!")
            continue

        match = _match_fingerprint(cname)
        if match:
            service = match["service"]
            fp = match["fingerprint"]
            if fp and _http_fingerprint_check(sub, fp):
                print(f"    !! CONFIRMED takeover ({service}): fingerprint matched")
            else:
                print(f"    ? Potential takeover ({service}): needs manual check")
        else:
            print("    OK — target resolves, no known vulnerable service")

    if found_cnames == 0:
        print("No CNAME records found for tested subdomains.")
