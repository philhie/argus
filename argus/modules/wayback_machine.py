"""M21: Wayback Machine Historical Exposure Check.

Queries the Wayback Machine CDX API for historically exposed sensitive files.

Usage: python -m argus.modules.wayback_machine example.com
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.wayback_machine")

CDX_API = "https://web.archive.org/cdx/search/cdx"
CDX_TIMEOUT = 60

SENSITIVE_PATTERNS = [
    (re.compile(r'\.env(\b|$)'), "ENV-Datei", Severity.CRITICAL),
    (re.compile(r'\.git/'), "Git-Repository", Severity.CRITICAL),
    (re.compile(r'\.sql(\b|$)'), "SQL-Dump", Severity.CRITICAL),
    (re.compile(r'wp-config\.php'), "WordPress-Config", Severity.CRITICAL),
    (re.compile(r'\.bak(\b|$)'), "Backup-Datei", Severity.HIGH),
    (re.compile(r'\.log(\b|$)'), "Log-Datei", Severity.HIGH),
    (re.compile(r'/phpmyadmin', re.I), "phpMyAdmin", Severity.HIGH),
    (re.compile(r'/adminer', re.I), "Adminer", Severity.HIGH),
    (re.compile(r'/admin(?:/|$)'), "Admin-Panel", Severity.MEDIUM),
    (re.compile(r'/debug'), "Debug-Endpoint", Severity.HIGH),
    (re.compile(r'/swagger|/api-doc|/openapi', re.I), "API-Dokumentation", Severity.MEDIUM),
    (re.compile(r'sitemap.*\.xml', re.I), "Sitemap", Severity.INFO),
    (re.compile(r'web\.config$'), "IIS-Konfiguration", Severity.HIGH),
    (re.compile(r'server-status'), "Apache Server-Status", Severity.HIGH),
    (re.compile(r'\.map$'), "Source Map", Severity.MEDIUM),
    (re.compile(r'phpinfo'), "PHP Info", Severity.HIGH),
]

NIS2_REF = "§30 Abs. 2 Nr. 5"


def _query_cdx(domain: str) -> list[list[str]]:
    """Query the Wayback Machine CDX API. Returns rows of [original, statuscode, mimetype]."""
    params = {
        "url": f"{domain}/*",
        "output": "json",
        "fl": "original,statuscode,mimetype",
        "collapse": "urlkey",
        "limit": "10000",
    }
    try:
        resp = requests.get(CDX_API, params=params, timeout=CDX_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("CDX-API-Anfrage fehlgeschlagen für %s: %s", domain, exc)
        return []

    if not data or len(data) < 2:
        return []

    # First row is the header, skip it
    return data[1:]


def _check_still_live(url: str) -> bool:
    """HEAD request to check if a URL is still reachable (HTTP 200)."""
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def _match_pattern(url: str) -> tuple[str, str, Severity] | None:
    """Match a URL against sensitive patterns. Returns (pattern_name, url, severity) or None."""
    for pattern, name, severity in SENSITIVE_PATTERNS:
        if pattern.search(url):
            return name, url, severity
    return None


def scan_wayback(domain: str) -> list[Finding]:
    """Query Wayback Machine and analyse results for sensitive file exposure."""
    findings: list[Finding] = []
    rows = _query_cdx(domain)

    if not rows:
        logger.info("Keine Wayback-Machine-Ergebnisse für %s", domain)
        return findings

    # Collect matches grouped by pattern name for deduplication
    matches_by_pattern: dict[str, list[tuple[str, Severity]]] = defaultdict(list)

    for row in rows:
        if len(row) < 3:
            continue
        original_url = row[0]
        match = _match_pattern(original_url)
        if match:
            pattern_name, url, severity = match
            matches_by_pattern[pattern_name].append((url, severity))

    # Process each pattern group
    for pattern_name, matched_urls in matches_by_pattern.items():
        severity = matched_urls[0][1]
        count = len(matched_urls)
        # Pick the first URL as representative example
        representative_url = matched_urls[0][0]

        # For CRITICAL/HIGH: check if still live
        if severity in (Severity.CRITICAL, Severity.HIGH):
            still_live = _check_still_live(representative_url)

            if still_live:
                findings.append(Finding(
                    id="WB-001",
                    module="wayback_machine",
                    category="web_application",
                    title=f"Historisch exponierte Datei noch erreichbar: {representative_url}",
                    description=(
                        f"Die Datei ({pattern_name}) wurde im Webarchiv gefunden und ist "
                        f"aktuell noch unter der Original-URL erreichbar. "
                        f"Ein Angreifer kann diese Datei direkt abrufen."
                    ),
                    severity=Severity.CRITICAL,
                    evidence=(
                        f"Wayback Machine CDX: {count} URL(s) für Muster '{pattern_name}'. "
                        f"HEAD {representative_url} → HTTP 200 (noch live)"
                    ),
                    nis2_paragraphs=[NIS2_REF],
                    remediation=(
                        f"Zugriff auf {pattern_name}-Dateien sofort blockieren. "
                        f"Exponierte Credentials rotieren. Webarchiv-Löschung bei archive.org beantragen."
                    ),
                ))
                continue

        # Not live or lower severity — report as archived finding (deduplicated)
        if count == 1:
            title = f"{pattern_name} im Webarchiv gefunden: {representative_url}"
        else:
            title = f"{count}x {pattern_name} im Webarchiv gefunden (z.B. {representative_url})"

        findings.append(Finding(
            id="WB-002",
            module="wayback_machine",
            category="web_application",
            title=title,
            description=(
                f"{count} URL(s) mit Muster '{pattern_name}' im Wayback Machine Archiv gefunden. "
                f"Diese Dateien waren historisch öffentlich zugänglich. "
                f"Prüfen Sie, ob sensible Daten exponiert wurden."
            ),
            severity=severity,
            evidence=(
                f"Wayback Machine CDX: {count} URL(s) für Muster '{pattern_name}'. "
                f"Beispiel: {representative_url}"
            ),
            nis2_paragraphs=[NIS2_REF],
            remediation=(
                f"Historisch exponierte {pattern_name}-Dateien prüfen. "
                f"Falls Credentials enthalten: sofort rotieren. "
                f"Löschung aus dem Webarchiv bei archive.org beantragen."
            ),
        ))

    # WB-003: Summary finding if many sensitive URLs
    total_sensitive = sum(len(urls) for urls in matches_by_pattern.values())
    if total_sensitive > 10:
        findings.append(Finding(
            id="WB-003",
            module="wayback_machine",
            category="web_application",
            title=f"{total_sensitive} sensitive URLs im Webarchiv für {domain}",
            description=(
                f"Insgesamt {total_sensitive} URLs mit sensitiven Mustern wurden im "
                f"Wayback Machine Archiv für {domain} gefunden. "
                f"Dies deutet auf wiederkehrende Konfigurationsprobleme hin."
            ),
            severity=Severity.MEDIUM,
            evidence=(
                f"Wayback Machine CDX: {total_sensitive} sensitive URLs gefunden. "
                f"Muster: {', '.join(matches_by_pattern.keys())}"
            ),
            nis2_paragraphs=[NIS2_REF],
            remediation=(
                "Umfassende Überprüfung der Webserver-Konfiguration durchführen. "
                "Sicherstellen, dass keine sensitiven Dateien öffentlich zugänglich sind. "
                "CI/CD-Pipeline um automatische Prüfungen erweitern."
            ),
        ))

    return findings


@register
class WaybackMachineModule(BaseModule):
    name = "wayback_machine"
    description = "Wayback Machine Historical Exposure"
    phase = 5
    step = 7

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_wayback(domain)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.wayback_machine <domain>")
        sys.exit(1)

    target = sys.argv[1]
    if target.startswith("http"):
        # Strip protocol for CDX query
        target = target.split("//", 1)[1].rstrip("/")

    print(f"Querying Wayback Machine for {target}...")
    results = scan_wayback(target)

    if not results:
        print("Keine sensitiven URLs im Webarchiv gefunden.")
    else:
        for f in results:
            print(f"  [{f.severity.value}] {f.id}: {f.title}")
            print(f"    {f.evidence}")
        print(f"\n{len(results)} Finding(s)")
