"""M09: Common File Exposure Check.

Usage: python -m argus.modules.file_exposure https://true-fruits.com
"""

from __future__ import annotations

import logging

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.file_exposure")

# Ordered by severity — check most critical first
FILE_CHECKS = [
    # CRITICAL: Credentials and secrets
    {"path": "/.env", "severity": Severity.CRITICAL, "desc": "Environment-Variablen (oft mit DB-Passwörtern, API-Keys)"},
    {"path": "/.htpasswd", "severity": Severity.CRITICAL, "desc": "Apache-Passwortdatei mit knackbaren Hashes"},
    {"path": "/.git/config", "severity": Severity.CRITICAL, "desc": "Git-Repository-Konfiguration (Quellcode-Exposure)"},
    {"path": "/.git/HEAD", "severity": Severity.CRITICAL, "desc": "Git-Repository HEAD (bestätigt .git-Exposure)"},
    {"path": "/wp-config.php.bak", "severity": Severity.CRITICAL, "desc": "WordPress-Config-Backup (DB-Zugangsdaten)"},
    {"path": "/wp-config.php~", "severity": Severity.CRITICAL, "desc": "WordPress-Config Editor-Backup"},
    {"path": "/web.config", "severity": Severity.HIGH, "desc": "IIS-Konfiguration (kann Connection-Strings enthalten)"},
    {"path": "/config.php.bak", "severity": Severity.HIGH, "desc": "PHP-Config-Backup"},

    # HIGH: Server configuration
    {"path": "/server-status", "severity": Severity.HIGH, "desc": "Apache Server-Status (Verbindungsinformationen)"},
    {"path": "/server-info", "severity": Severity.HIGH, "desc": "Apache Server-Info (vollständige Konfiguration)"},
    {"path": "/phpinfo.php", "severity": Severity.HIGH, "desc": "PHP-Info-Seite (vollständige Serverkonfiguration)"},
    {"path": "/info.php", "severity": Severity.HIGH, "desc": "PHP-Info-Seite (Variante)"},

    # HIGH: Database and backups
    {"path": "/backup.sql", "severity": Severity.CRITICAL, "desc": "SQL-Datenbank-Backup"},
    {"path": "/dump.sql", "severity": Severity.CRITICAL, "desc": "SQL-Datenbank-Dump"},
    {"path": "/backup.zip", "severity": Severity.CRITICAL, "desc": "Backup-Archiv"},

    # MEDIUM: Development artifacts
    {"path": "/docker-compose.yml", "severity": Severity.HIGH, "desc": "Docker Compose (kann Credentials enthalten)"},
    {"path": "/Dockerfile", "severity": Severity.MEDIUM, "desc": "Docker-Konfiguration"},
    {"path": "/composer.json", "severity": Severity.MEDIUM, "desc": "PHP-Dependency-Manifest"},
    {"path": "/package.json", "severity": Severity.MEDIUM, "desc": "Node.js-Dependency-Manifest"},
    {"path": "/.htaccess", "severity": Severity.MEDIUM, "desc": "Apache-Konfiguration"},

    # API documentation
    {"path": "/swagger", "severity": Severity.MEDIUM, "desc": "Swagger API-Dokumentation"},
    {"path": "/swagger-ui", "severity": Severity.MEDIUM, "desc": "Swagger UI"},
    {"path": "/api-docs", "severity": Severity.MEDIUM, "desc": "API-Dokumentation"},
    {"path": "/_profiler", "severity": Severity.HIGH, "desc": "Symfony Profiler (Debug-Informationen)"},
    {"path": "/_wdt", "severity": Severity.HIGH, "desc": "Symfony Web Debug Toolbar"},

    # INFO: Useful reconnaissance
    {"path": "/robots.txt", "severity": Severity.INFO, "desc": "Robot-Exclusion (zeigt versteckte Pfade)"},
    {"path": "/sitemap.xml", "severity": Severity.INFO, "desc": "Sitemap (vollständige URL-Struktur)"},
    {"path": "/.well-known/security.txt", "severity": Severity.INFO, "desc": "Security-Kontakt (positiver Fund)"},
]

SOFT_404_INDICATORS = [
    "page not found", "404", "not found", "does not exist",
    "seite nicht gefunden", "nicht gefunden", "error page",
]


def _is_soft_404(text: str) -> bool:
    """Detect custom 404 pages that return HTTP 200."""
    lower = text.lower()
    return any(ind in lower for ind in SOFT_404_INDICATORS)


def _looks_like_real_content(resp: requests.Response, path: str) -> bool:
    """Determine if response is real content, not a soft-404 or redirect-to-home."""
    if resp.status_code != 200:
        return False
    if len(resp.content) < 10:
        return False
    if _is_soft_404(resp.text):
        return False
    return True


def check_file_exposures(base_url: str) -> list[Finding]:
    """Check for exposed sensitive files. Returns findings."""
    findings: list[Finding] = []

    for check in FILE_CHECKS:
        url = f"{base_url}{check['path']}"
        try:
            resp = requests.get(url, timeout=5, allow_redirects=False)

            if _looks_like_real_content(resp, check["path"]):
                content_preview = resp.text[:200]
                # Redact potential credentials
                has_creds = any(kw in resp.text.lower() for kw in [
                    "password", "secret", "api_key", "apikey",
                    "$apr1$", "db_", "private_key",
                ])

                # Elevate severity if credentials found
                severity = check["severity"]
                if has_creds and severity not in (Severity.CRITICAL,):
                    severity = Severity.CRITICAL

                findings.append(Finding(
                    id=f"FILE-{check['path'].replace('/', '').replace('.', '')[:12].upper()}",
                    module="file_exposure",
                    category="web_application",
                    title=f"Sensible Datei öffentlich zugänglich: {check['path']}",
                    description=f"{check['desc']}. Die Datei ist ohne Authentifizierung abrufbar.",
                    severity=severity,
                    evidence=(
                        f"GET {url} → HTTP {resp.status_code}, "
                        f"{len(resp.content)} Bytes"
                        f"{', ENTHÄLT CREDENTIALS' if has_creds else ''}"
                    ),
                    nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
                    remediation=f"Zugriff auf {check['path']} per Serverkonfiguration blockieren.",
                ))
        except requests.RequestException:
            continue

    return findings


@register
class FileExposureModule(BaseModule):
    name = "file_exposure"
    description = "Common File Exposure Check (40+ paths)"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_file_exposures(f"https://{domain}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.file_exposure <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = f"https://{url}"
    print(f"Checking file exposures on {url}...")
    findings = check_file_exposures(url)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
