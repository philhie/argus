"""M20: GitHub Secret Scanning — searches public repos for leaked credentials.

Usage: python -m argus.modules.github_secrets <domain>
"""

from __future__ import annotations

import logging
import time

import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.github_secrets")

DORK_PATTERNS = [
    ('"{domain}" password', "Passwort"),
    ('"{domain}" api_key', "API-Key"),
    ('"{domain}" secret', "Secret"),
    ('"{domain}" token', "Token"),
    ('"{domain}" AWS_ACCESS_KEY', "AWS-Zugangsdaten"),
    ('"{domain}" PRIVATE KEY', "Privater Schlüssel"),
    ('"{domain}" jdbc:', "Datenbank-Verbindung"),
    ('"{domain}" mongodb://', "MongoDB-URI"),
    ('"{domain}" smtp_password', "SMTP-Passwort"),
    ('"{domain}" DB_PASSWORD', "Datenbank-Passwort"),
    ('"{domain}" Authorization', "Authorization-Header"),
    ('"{domain}" client_secret', "Client Secret"),
]

# Map dork keywords to finding IDs and severities
_CLASSIFICATION: dict[str, tuple[str, Severity]] = {
    "PRIVATE KEY": ("GH-001", Severity.CRITICAL),
    "api_key": ("GH-002", Severity.CRITICAL),
    "token": ("GH-002", Severity.CRITICAL),
    "secret": ("GH-002", Severity.CRITICAL),
    "client_secret": ("GH-002", Severity.CRITICAL),
    "Authorization": ("GH-002", Severity.CRITICAL),
    "jdbc:": ("GH-003", Severity.CRITICAL),
    "mongodb://": ("GH-003", Severity.CRITICAL),
    "DB_PASSWORD": ("GH-003", Severity.CRITICAL),
    "smtp_password": ("GH-004", Severity.HIGH),
    "AWS_ACCESS_KEY": ("GH-005", Severity.CRITICAL),
    "password": ("GH-006", Severity.MEDIUM),
}

_TITLE_TEMPLATES: dict[str, str] = {
    "GH-001": "Privater Schlüssel auf GitHub: {repo}/{file}",
    "GH-002": "API-Key/Token auf GitHub exponiert: {repo}/{file}",
    "GH-003": "Datenbank-Credentials auf GitHub: {repo}/{file}",
    "GH-004": "E-Mail-Credentials auf GitHub: {repo}/{file}",
    "GH-005": "AWS-Zugangsdaten auf GitHub: {repo}/{file}",
    "GH-006": "Potentielles Secret auf GitHub: {repo}/{file}",
}

_DESCRIPTION_TEMPLATES: dict[str, str] = {
    "GH-001": (
        "Ein privater Schlüssel mit Bezug zu {domain} wurde in einem öffentlichen "
        "GitHub-Repository gefunden. Private Schlüssel ermöglichen die vollständige "
        "Übernahme der betroffenen Systeme oder Verschlüsselung."
    ),
    "GH-002": (
        "Ein API-Key oder Token mit Bezug zu {domain} wurde in einem öffentlichen "
        "GitHub-Repository gefunden. Solche Zugangsdaten können für unbefugten "
        "Zugriff auf Dienste und Daten missbraucht werden."
    ),
    "GH-003": (
        "Datenbank-Zugangsdaten mit Bezug zu {domain} wurden in einem öffentlichen "
        "GitHub-Repository gefunden. Angreifer können diese für direkten Zugriff "
        "auf Datenbanken nutzen."
    ),
    "GH-004": (
        "E-Mail-/SMTP-Zugangsdaten mit Bezug zu {domain} wurden in einem öffentlichen "
        "GitHub-Repository gefunden. Diese ermöglichen den Versand von E-Mails "
        "im Namen der Organisation."
    ),
    "GH-005": (
        "AWS-Zugangsdaten mit Bezug zu {domain} wurden in einem öffentlichen "
        "GitHub-Repository gefunden. AWS-Keys ermöglichen vollen Zugriff auf "
        "Cloud-Ressourcen und können zu erheblichem finanziellen Schaden führen."
    ),
    "GH-006": (
        "Ein potentielles Secret (Passwort) mit Bezug zu {domain} wurde in einem "
        "öffentlichen GitHub-Repository gefunden. Dieses sollte überprüft und "
        "ggf. rotiert werden."
    ),
}

_REMEDIATION_TEMPLATES: dict[str, str] = {
    "GH-001": (
        "Den privaten Schlüssel sofort widerrufen und neu generieren. "
        "Die betroffene Datei aus der Git-Historie entfernen (git filter-branch "
        "oder BFG Repo-Cleaner). Secret-Scanning im Repository aktivieren."
    ),
    "GH-002": (
        "Den API-Key/Token sofort rotieren und den alten invalidieren. "
        "Die betroffene Datei aus der Git-Historie entfernen. "
        "Secrets künftig über Umgebungsvariablen oder einen Secret-Manager bereitstellen."
    ),
    "GH-003": (
        "Das Datenbank-Passwort sofort ändern und den Zugriff von den betroffenen "
        "IPs einschränken. Die Zugangsdaten aus der Git-Historie entfernen. "
        "Prüfen, ob unautorisierter Zugriff stattgefunden hat."
    ),
    "GH-004": (
        "Das SMTP-Passwort sofort ändern. Prüfen, ob über den Zugang Spam "
        "oder Phishing-Mails versendet wurden. Die Zugangsdaten aus der "
        "Git-Historie entfernen."
    ),
    "GH-005": (
        "Die AWS-Zugangsdaten sofort deaktivieren und neue generieren. "
        "CloudTrail-Logs auf unautorisierte Aktivitäten prüfen. "
        "IAM-Berechtigungen nach dem Least-Privilege-Prinzip einschränken."
    ),
    "GH-006": (
        "Das betroffene Passwort sofort ändern. Die Datei aus der Git-Historie "
        "entfernen. Prüfen, ob der Zugang missbraucht wurde. "
        "Secret-Scanning im Repository aktivieren."
    ),
}

GITHUB_CODE_SEARCH_URL = "https://api.github.com/search/code"


def _classify_dork(query: str) -> tuple[str, Severity]:
    """Classify a dork query to a finding ID and severity.

    More specific patterns are checked first to avoid false matches
    (e.g. 'client_secret' before 'secret').
    """
    # Check more specific patterns first
    ordered_keywords = [
        "PRIVATE KEY",
        "AWS_ACCESS_KEY",
        "client_secret",
        "api_key",
        "DB_PASSWORD",
        "smtp_password",
        "mongodb://",
        "jdbc:",
        "Authorization",
        "token",
        "secret",
        "password",
    ]
    for keyword in ordered_keywords:
        if keyword in query:
            return _CLASSIFICATION[keyword]
    return ("GH-006", Severity.MEDIUM)


def scan_github_secrets(domain: str) -> list[Finding]:
    """Search GitHub Code Search for leaked secrets referencing the domain."""
    findings: list[Finding] = []

    if not settings.github_token:
        logger.info(
            "Kein GitHub-Token konfiguriert — Modul wird übersprungen"
        )
        return findings

    headers = {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    seen_urls: set[str] = set()

    for idx, (pattern, label) in enumerate(DORK_PATTERNS):
        query = pattern.replace("{domain}", domain)

        if idx > 0:
            time.sleep(6.5)  # Rate limit: 10 req/min for authenticated code search

        logger.debug("GitHub Code Search: %s", query)

        try:
            resp = requests.get(
                GITHUB_CODE_SEARCH_URL,
                params={"q": query, "per_page": 5},
                headers=headers,
                timeout=15,
            )
        except requests.RequestException as e:
            logger.warning("GitHub API Anfrage fehlgeschlagen: %s", e)
            continue

        if resp.status_code == 403:
            logger.warning(
                "GitHub Rate-Limit erreicht (403) — "
                "verbleibende Dork-Patterns werden übersprungen"
            )
            break

        if resp.status_code == 422:
            logger.debug(
                "GitHub hat die Abfrage abgelehnt (422) für: %s", query
            )
            continue

        if resp.status_code != 200:
            logger.warning(
                "GitHub API Fehler %d für Abfrage: %s", resp.status_code, query
            )
            continue

        try:
            data = resp.json()
        except ValueError:
            logger.warning("GitHub API Antwort ist kein gültiges JSON")
            continue

        total_count = data.get("total_count", 0)
        if total_count == 0:
            continue

        logger.info(
            "GitHub-Treffer für '%s': %d Ergebnis(se)", label, total_count
        )

        items = data.get("items", [])
        finding_id, severity = _classify_dork(query)

        for item in items:
            repo_name = item.get("repository", {}).get("full_name", "unbekannt")
            file_path = item.get("path", "unbekannt")
            html_url = item.get("html_url", "")

            # Deduplicate by URL
            if html_url in seen_urls:
                continue
            seen_urls.add(html_url)

            title = _TITLE_TEMPLATES[finding_id].format(
                repo=repo_name, file=file_path
            )
            description = _DESCRIPTION_TEMPLATES[finding_id].format(
                domain=domain
            )
            remediation = _REMEDIATION_TEMPLATES[finding_id]

            findings.append(Finding(
                id=finding_id,
                module="github_secrets",
                category="credential_exposure",
                title=title,
                description=description,
                severity=severity,
                evidence=(
                    f"GitHub Code Search: q={query} → "
                    f"{repo_name}/{file_path} — {html_url}"
                ),
                nis2_paragraphs=["§30 Abs. 2 Nr. 7"],
                remediation=remediation,
            ))

    logger.info(
        "GitHub Secret Scanning abgeschlossen: %d Finding(s)", len(findings)
    )
    return findings


@register
class GithubSecretsModule(BaseModule):
    name = "github_secrets"
    description = "GitHub Secret Scanning"
    phase = 5
    step = 7

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_github_secrets(domain)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.github_secrets <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"GitHub Secret Scanning für {domain}...")

    ctx = ScanContext(domain=domain)
    results = scan_github_secrets(domain)

    print(f"\n{'=' * 60}")
    print(f"GitHub Secret Scanning Ergebnisse für {domain}")
    print(f"{'=' * 60}")
    print(f"Findings: {len(results)}")

    for f in results:
        print(f"\n  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")

    if not results:
        print("\n  Keine Secrets auf GitHub gefunden.")

    print()
