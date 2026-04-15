"""M11: API Endpoint Discovery.

Finds exposed API documentation, health endpoints, and Spring Actuator.
Excludes paths already checked by file_exposure.py (/swagger, /swagger-ui, /api-docs)
and graphql_introspection.py (/graphql, /graphiql, etc.).

Usage: python -m argus.modules.api_discovery https://example.com
"""

from __future__ import annotations

import logging

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.api_discovery")

# API endpoints to probe, grouped by type
# Excludes: /swagger, /swagger-ui, /api-docs (file_exposure.py)
# Excludes: /graphql, /graphiql, /api/graphql, /v1/graphql (graphql_introspection.py)
API_PATHS = [
    # Swagger / OpenAPI (paths NOT in file_exposure.py)
    {"path": "/swagger-ui.html", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ["swagger-ui", "Swagger UI", "swagger-resources"]},
    {"path": "/swagger-ui/index.html", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ["swagger-ui", "Swagger UI"]},
    {"path": "/openapi.json", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ['"openapi"', '"paths"', '"info"']},
    {"path": "/openapi.yaml", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ["openapi:", "paths:", "info:"]},
    {"path": "/redoc", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ["redoc", "ReDoc", "Redoc"]},
    {"path": "/v2/api-docs", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ['"swagger"', '"paths"', '"basePath"']},
    {"path": "/v3/api-docs", "type": "docs", "severity": Severity.MEDIUM,
     "markers": ['"openapi"', '"paths"']},
    # REST API endpoints
    {"path": "/api/v1", "type": "rest", "severity": Severity.MEDIUM,
     "markers": []},
    {"path": "/api/v2", "type": "rest", "severity": Severity.MEDIUM,
     "markers": []},
    {"path": "/rest", "type": "rest", "severity": Severity.MEDIUM,
     "markers": []},
    # Health / Status
    {"path": "/api/health", "type": "health", "severity": Severity.LOW,
     "markers": ["status", "healthy", "ok", "UP"]},
    {"path": "/api/status", "type": "health", "severity": Severity.LOW,
     "markers": ["status", "version", "uptime"]},
    {"path": "/health", "type": "health", "severity": Severity.LOW,
     "markers": ["status", "healthy", "ok", "UP"]},
    {"path": "/healthz", "type": "health", "severity": Severity.LOW,
     "markers": ["ok", "healthy"]},
    # Spring Actuator (severity escalated per endpoint)
    {"path": "/actuator", "type": "actuator", "severity": Severity.MEDIUM,
     "markers": ["_links", "self", "href"]},
    {"path": "/actuator/health", "type": "actuator", "severity": Severity.LOW,
     "markers": ["status"]},
    {"path": "/actuator/info", "type": "actuator", "severity": Severity.LOW,
     "markers": []},
    {"path": "/actuator/env", "type": "actuator_sensitive", "severity": Severity.HIGH,
     "markers": ["propertySources", "activeProfiles", "property"]},
    {"path": "/actuator/beans", "type": "actuator_sensitive", "severity": Severity.HIGH,
     "markers": ["contexts", "beans"]},
    {"path": "/actuator/configprops", "type": "actuator_sensitive", "severity": Severity.HIGH,
     "markers": ["contexts", "beans"]},
    {"path": "/actuator/mappings", "type": "actuator_sensitive", "severity": Severity.HIGH,
     "markers": ["contexts", "dispatcherServlets"]},
]

# Finding ID by type
_FINDING_IDS = {
    "docs": "API-001",
    "health": "API-002",
    "actuator": "API-003",
    "actuator_sensitive": "API-003",
    "rest": "API-004",
}

SOFT_404_INDICATORS = [
    "page not found", "404", "not found", "does not exist",
    "seite nicht gefunden", "nicht gefunden", "error page",
    "the page you", "oops", "nothing here",
]


def _is_soft_404(text: str) -> bool:
    lower = text.lower()
    return any(ind in lower for ind in SOFT_404_INDICATORS)


def _has_markers(text: str, markers: list[str]) -> bool:
    """Check if response text contains any expected content markers."""
    if not markers:
        return True  # No markers required — accept any non-404 content
    return any(marker in text for marker in markers)


def _looks_like_api_content(resp: requests.Response, check: dict) -> bool:
    """Validate that a 200 response contains real API content."""
    if len(resp.content) < 10:
        return False
    if _is_soft_404(resp.text[:2000]):
        return False
    if check["markers"] and not _has_markers(resp.text[:5000], check["markers"]):
        return False
    return True


def check_api_endpoints(base_url: str) -> list[Finding]:
    """Probe for API endpoints on the given base URL."""
    findings: list[Finding] = []

    for check in API_PATHS:
        url = base_url.rstrip("/") + check["path"]

        try:
            resp = requests.get(url, timeout=5, allow_redirects=True, verify=True)
        except requests.RequestException:
            continue

        if resp.status_code != 200:
            continue

        if not _looks_like_api_content(resp, check):
            continue

        path = check["path"]
        ep_type = check["type"]
        finding_id = _FINDING_IDS[ep_type]
        path_slug = path.lstrip("/").replace("/", "-")[:20]

        # Build type-specific finding
        if ep_type == "docs":
            title = f"API-Dokumentation öffentlich zugänglich: {path}"
            desc = (
                f"Unter {path} ist eine API-Dokumentation (Swagger/OpenAPI) öffentlich "
                f"einsehbar. Dies offenbart die gesamte API-Struktur einschließlich "
                f"Endpunkten, Parametern und Datenmodellen."
            )
            remediation = (
                "API-Dokumentation nur intern oder authentifiziert bereitstellen. "
                "In Produktionsumgebungen Swagger/OpenAPI deaktivieren."
            )
        elif ep_type in ("actuator", "actuator_sensitive"):
            sensitive = ep_type == "actuator_sensitive"
            title = f"Spring Actuator öffentlich erreichbar: {path}"
            if sensitive:
                desc = (
                    f"Der Spring Actuator-Endpoint {path} ist öffentlich erreichbar und "
                    f"gibt sensible Konfigurationsdaten preis. Dies kann "
                    f"Datenbankpasswörter, API-Keys und interne Konfiguration offenlegen."
                )
            else:
                desc = (
                    f"Der Spring Actuator-Endpoint {path} ist öffentlich erreichbar. "
                    f"Actuator-Endpoints können interne Anwendungsinformationen offenlegen."
                )
            remediation = (
                "Spring Actuator-Endpoints absichern. Sensitive Endpoints "
                "(env, beans, configprops) in application.properties deaktivieren "
                "oder per Spring Security schützen."
            )
        elif ep_type == "health":
            title = f"API-Health/Status-Endpoint exponiert: {path}"
            desc = (
                f"Unter {path} ist ein Health- oder Status-Endpoint erreichbar. "
                f"Dies kann Informationen über die verwendete Technologie und "
                f"den Serverstatus preisgeben."
            )
            remediation = (
                "Health-/Status-Endpoints nur aus internen Netzwerken oder "
                "mit Authentifizierung erreichbar machen."
            )
        else:  # rest
            title = f"REST-API-Endpoint ohne erkennbare Authentifizierung: {path}"
            desc = (
                f"Unter {path} antwortet ein REST-API-Endpoint ohne "
                f"Authentifizierungsanforderung. Unauthentifizierte APIs können "
                f"Datenlecks oder unautorisierten Zugriff ermöglichen."
            )
            remediation = (
                "API-Endpoints mit Authentifizierung (API-Key, OAuth2, JWT) absichern."
            )

        content_preview = resp.text[:100].replace("\n", " ").strip()
        findings.append(Finding(
            id=f"{finding_id}-{path_slug}",
            module="api_discovery",
            category="web_application",
            title=title,
            description=desc,
            severity=check["severity"],
            evidence=f"GET {url} → HTTP {resp.status_code}, {len(resp.content)} Bytes, Inhalt: {content_preview!r}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 9"],
            remediation=remediation,
        ))

    return findings


@register
class ApiDiscoveryModule(BaseModule):
    name = "api_discovery"
    description = "API Endpoint Discovery (Swagger, Actuator, REST)"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_api_endpoints(f"https://{domain}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    target = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    if not target.startswith("http"):
        target = f"https://{target}"

    results = check_api_endpoints(target)
    print(f"\n{len(results)} Findings:")
    for f in results:
        print(f"  [{f.severity.value}] {f.title}")
        print(f"    {f.evidence}")
