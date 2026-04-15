"""M23: Google Dorking (Indexed Exposure) — SerpAPI-based dork queries.

Usage: python -m argus.modules.google_dorking <domain>
"""

from __future__ import annotations

import logging

import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.google_dorking")

# (query_template, german_title, severity)
DORK_QUERIES: list[tuple[str, str, Severity]] = [
    ('site:{domain} filetype:pdf "vertraulich" OR "intern" OR "confidential"', "Vertrauliche PDFs", Severity.HIGH),
    ('site:{domain} filetype:xls OR filetype:xlsx', "Excel-Dateien", Severity.MEDIUM),
    ('site:{domain} filetype:doc OR filetype:docx', "Word-Dokumente", Severity.INFO),
    ('site:{domain} intitle:"Index of"', "Directory Listing", Severity.HIGH),
    ('site:{domain} inurl:admin', "Admin-Panel", Severity.MEDIUM),
    ('site:{domain} inurl:login', "Login-Seite", Severity.INFO),
    ('site:{domain} inurl:backup OR inurl:bak', "Backup-Dateien", Severity.HIGH),
    ('site:{domain} ext:sql OR ext:bak OR ext:log', "Datenbank-/Backup-/Log-Dateien", Severity.CRITICAL),
    ('site:{domain} "phpinfo()"', "PHP Info", Severity.HIGH),
    ('"{domain}" inurl:jira OR inurl:confluence', "Entwicklungstools", Severity.MEDIUM),
    ('"{domain}" inurl:gitlab OR inurl:jenkins', "CI/CD-Tools", Severity.MEDIUM),
    ('site:{domain} inurl:api inurl:swagger OR inurl:openapi', "API-Dokumentation", Severity.MEDIUM),
]

SERPAPI_URL = "https://serpapi.com/search.json"


def scan_google_dorking(domain: str, context: ScanContext) -> list[Finding]:
    """Execute Google dork queries via SerpAPI and generate findings."""
    findings: list[Finding] = []

    if not settings.serpapi_key:
        logger.info("Kein SerpAPI-Key konfiguriert — Modul wird übersprungen")
        return findings

    logger.info("Google Dorking für %s mit %d Dork-Abfragen", domain, len(DORK_QUERIES))

    for idx, (query_template, title, severity) in enumerate(DORK_QUERIES):
        query = query_template.format(domain=domain)
        finding_id = f"GORK-{idx + 1:03d}"

        try:
            resp = requests.get(
                SERPAPI_URL,
                params={
                    "q": query,
                    "api_key": settings.serpapi_key,
                    "num": 10,
                },
                timeout=settings.request_timeout,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(
                "SerpAPI-Fehler bei Dork '%s': %s", title, e,
            )
            continue

        try:
            data = resp.json()
        except ValueError:
            logger.warning(
                "SerpAPI-Antwort für '%s' ist kein gültiges JSON", title,
            )
            continue

        organic_results = data.get("organic_results", [])
        if not organic_results:
            logger.debug("Keine Ergebnisse für Dork '%s'", title)
            continue

        # Build evidence from the results
        result_lines: list[str] = []
        for result in organic_results[:10]:
            r_title = result.get("title", "Ohne Titel")
            r_link = result.get("link", "")
            r_snippet = result.get("snippet", "")
            result_lines.append(f"  - {r_title}: {r_link}")
            if r_snippet:
                result_lines.append(f"    Snippet: {r_snippet[:150]}")

        evidence_text = (
            f"Google Dork: {query}\n"
            f"{len(organic_results)} Treffer gefunden:\n"
            + "\n".join(result_lines)
        )

        findings.append(Finding(
            id=finding_id,
            module="google_dorking",
            category="web_application",
            title=f"{title} — {len(organic_results)} indexierte Treffer für {domain}",
            description=(
                f"Die Google-Suche mit dem Dork '{query}' hat "
                f"{len(organic_results)} öffentlich indexierte Ergebnisse ergeben. "
                f"Sensible oder interne Inhalte sollten nicht über Suchmaschinen "
                f"auffindbar sein."
            ),
            severity=severity,
            evidence=evidence_text,
            nis2_paragraphs=["§30 Abs. 2 Nr. 5"],
            remediation=(
                "Prüfen Sie die gefundenen Inhalte und entfernen Sie sensible "
                "Dateien aus dem öffentlichen Zugriff. Nutzen Sie robots.txt und "
                "noindex-Tags, um die Indexierung einzuschränken. Beantragen Sie "
                "die Entfernung aus dem Google-Index über die Search Console."
            ),
        ))

        logger.info(
            "Dork '%s': %d Treffer → %s (%s)",
            title, len(organic_results), finding_id, severity.value,
        )

    logger.info(
        "Google Dorking abgeschlossen: %d Finding(s) für %s",
        len(findings), domain,
    )

    return findings


@register
class GoogleDorkingModule(BaseModule):
    name = "google_dorking"
    description = "Google Dorking (Indexed Exposure)"
    phase = 5
    step = 8

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_google_dorking(domain, context)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.google_dorking <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Google Dorking für {domain}...")

    ctx = ScanContext(domain=domain)
    findings = scan_google_dorking(domain, ctx)

    print(f"\n{'='*60}")
    print(f"Google Dorking Ergebnisse für {domain}")
    print(f"{'='*60}")
    print(f"Findings ({len(findings)})")
    print(f"{'='*60}")

    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()

    if not findings:
        print("  Keine Findings — entweder keine Ergebnisse oder kein API-Key.")
