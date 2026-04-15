"""M10: Admin Panel Discovery.

Enumerates common admin panels, CMS login pages, and management interfaces.
Excludes paths already checked by file_exposure.py (/server-status, /server-info).

Usage: python -m argus.modules.admin_panel https://example.com
"""

from __future__ import annotations

import logging

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.admin_panel")

# Admin panel paths grouped by type
# Excludes /server-status, /server-info (already in file_exposure.py)
ADMIN_PATHS = [
    # CMS admin panels
    {"path": "/wp-admin", "type": "cms", "name": "WordPress", "severity": Severity.MEDIUM},
    {"path": "/wp-login.php", "type": "cms", "name": "WordPress", "severity": Severity.MEDIUM},
    {"path": "/typo3", "type": "cms", "name": "TYPO3", "severity": Severity.MEDIUM},
    {"path": "/administrator", "type": "cms", "name": "Joomla", "severity": Severity.MEDIUM},
    {"path": "/user/login", "type": "cms", "name": "Drupal", "severity": Severity.MEDIUM},
    {"path": "/contao", "type": "cms", "name": "Contao", "severity": Severity.MEDIUM},
    # Database admin panels
    {"path": "/phpmyadmin", "type": "database", "name": "phpMyAdmin", "severity": Severity.HIGH},
    {"path": "/phpMyAdmin", "type": "database", "name": "phpMyAdmin", "severity": Severity.HIGH},
    {"path": "/adminer", "type": "database", "name": "Adminer", "severity": Severity.HIGH},
    {"path": "/adminer.php", "type": "database", "name": "Adminer", "severity": Severity.HIGH},
    # Server management
    {"path": "/cpanel", "type": "management", "name": "cPanel", "severity": Severity.HIGH},
    {"path": "/webmail", "type": "management", "name": "Webmail", "severity": Severity.MEDIUM},
    {"path": "/plesk", "type": "management", "name": "Plesk", "severity": Severity.HIGH},
    {"path": ":2083", "type": "management", "name": "cPanel (Port 2083)", "severity": Severity.HIGH},
    # Generic admin
    {"path": "/admin", "type": "generic", "name": "Admin Panel", "severity": Severity.MEDIUM},
    {"path": "/admin/login", "type": "generic", "name": "Admin Login", "severity": Severity.MEDIUM},
    {"path": "/backend", "type": "generic", "name": "Backend", "severity": Severity.MEDIUM},
    {"path": "/dashboard", "type": "generic", "name": "Dashboard", "severity": Severity.MEDIUM},
]

# Finding ID by type
_FINDING_IDS = {
    "generic": "ADMIN-001",
    "database": "ADMIN-002",
    "management": "ADMIN-003",
    "cms": "ADMIN-004",
}

SOFT_404_INDICATORS = [
    "page not found", "404", "not found", "does not exist",
    "seite nicht gefunden", "nicht gefunden", "error page",
    "the page you", "oops", "nothing here",
]


def _is_soft_404(text: str) -> bool:
    lower = text.lower()
    return any(ind in lower for ind in SOFT_404_INDICATORS)


def _looks_like_real_content(resp: requests.Response) -> bool:
    if len(resp.content) < 50:
        return False
    if _is_soft_404(resp.text[:2000]):
        return False
    return True


def check_admin_panels(base_url: str) -> list[Finding]:
    """Probe for admin panels on the given base URL."""
    findings: list[Finding] = []

    for check in ADMIN_PATHS:
        path = check["path"]

        # Handle port-based checks (e.g. ":2083" for cPanel HTTPS)
        if path.startswith(":"):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            port = path.lstrip(":")
            url = f"https://{parsed.hostname}:{port}"
        else:
            url = base_url.rstrip("/") + path

        try:
            resp = requests.get(url, timeout=5, allow_redirects=False, verify=True)
        except requests.RequestException:
            continue

        found = False
        severity = check["severity"]

        if resp.status_code == 200:
            if _looks_like_real_content(resp):
                found = True
        elif resp.status_code in (301, 302, 303, 307, 308):
            # Redirect to login page confirms the panel exists
            location = resp.headers.get("Location", "").lower()
            if "login" in location or path.rstrip("/") + "/" in location:
                found = True
        elif resp.status_code == 403:
            # Forbidden confirms the path exists
            found = True
            severity = Severity.INFO  # Restricted access — lower severity

        if not found:
            continue

        panel_type = check["type"]
        finding_id = _FINDING_IDS[panel_type]
        path_slug = path.lstrip("/").replace("/", "-")[:15]

        # Generate per-type descriptions
        if panel_type == "database":
            title = f"Datenbank-Administrationspanel öffentlich erreichbar: {check['name']}"
            desc = (
                f"Das Datenbank-Administrationstool {check['name']} ist unter {path} "
                f"öffentlich erreichbar. Dies ermöglicht direkten Zugriff auf die Datenbank "
                f"und stellt ein kritisches Sicherheitsrisiko dar."
            )
        elif panel_type == "management":
            title = f"Server-Management-Panel öffentlich erreichbar: {check['name']}"
            desc = (
                f"Das Server-Management-Panel {check['name']} ist unter {path} "
                f"öffentlich erreichbar. Angreifer können versuchen, "
                f"Zugangsdaten zu erraten oder bekannte Schwachstellen auszunutzen."
            )
        elif panel_type == "cms":
            title = f"CMS-Login-Seite öffentlich erreichbar: {check['name']} ({path})"
            desc = (
                f"Die Login-Seite des CMS {check['name']} ist unter {path} erreichbar. "
                f"Dies ermöglicht Brute-Force-Angriffe auf das Administratorkonto."
            )
        else:
            title = f"Admin-Panel öffentlich erreichbar: {path}"
            desc = (
                f"Unter {path} wurde ein Admin-Panel gefunden (HTTP {resp.status_code}). "
                f"Öffentlich erreichbare Admin-Panels sind ein häufiges Angriffsziel."
            )

        evidence_parts = [f"GET {url} → HTTP {resp.status_code}"]
        if resp.status_code == 200:
            evidence_parts.append(f"{len(resp.content)} Bytes")
        elif resp.status_code in (301, 302, 303, 307, 308):
            evidence_parts.append(f"→ {resp.headers.get('Location', '?')}")

        findings.append(Finding(
            id=f"{finding_id}-{path_slug}",
            module="admin_panel",
            category="web_application",
            title=title,
            description=desc,
            severity=severity,
            evidence=", ".join(evidence_parts),
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation=(
                f"Admin-Panel {path} nicht öffentlich zugänglich machen. "
                f"Zugriff per VPN, IP-Whitelist oder .htaccess einschränken. "
                f"Multi-Faktor-Authentifizierung aktivieren."
            ),
        ))

    return findings


@register
class AdminPanelModule(BaseModule):
    name = "admin_panel"
    description = "Admin Panel Discovery (CMS, DB, Management)"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_admin_panels(f"https://{domain}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    if not target.startswith("http"):
        target = f"https://{target}"

    results = check_admin_panels(target)
    print(f"\n{len(results)} Findings:")
    for f in results:
        print(f"  [{f.severity.value}] {f.title}")
        print(f"    {f.evidence}")
