"""M29: GraphQL Introspection Exposure.

Usage: python -m argus.modules.graphql_introspection example.com
"""

from __future__ import annotations

import logging

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.graphql_introspection")

GRAPHQL_PATHS = ["/graphql", "/graphiql", "/api/graphql", "/v1/graphql", "/query"]

INTROSPECTION_QUERY = '{ __schema { types { name fields { name } } } }'
INTROSPECTION_QUERY_GET = "{__schema{types{name}}}"


def check_graphql_introspection(base_url: str) -> list[Finding]:
    """Test common GraphQL endpoint paths for introspection query exposure."""
    findings: list[Finding] = []

    for path in GRAPHQL_PATHS:
        url = f"{base_url}{path}"

        # Try POST with JSON body
        try:
            resp = requests.post(
                url,
                json={"query": INTROSPECTION_QUERY},
                headers={"Content-Type": "application/json"},
                timeout=10,
                allow_redirects=True,
            )
            if resp.status_code == 200 and '"__schema"' in resp.text:
                finding = _build_finding(url, resp)
                if finding:
                    findings.append(finding)
                    return findings  # One endpoint is enough proof
        except requests.RequestException:
            pass

        # Try GET with query parameter
        try:
            resp = requests.get(
                url,
                params={"query": INTROSPECTION_QUERY_GET},
                timeout=10,
                allow_redirects=True,
            )
            if resp.status_code == 200 and '"__schema"' in resp.text:
                finding = _build_finding(url, resp)
                if finding:
                    findings.append(finding)
                    return findings
        except requests.RequestException:
            pass

    return findings


def _build_finding(url: str, resp: requests.Response) -> Finding | None:
    """Build a finding from a successful introspection response."""
    type_count = 0
    field_count = 0

    try:
        data = resp.json()
        schema = data.get("data", {}).get("__schema", {})
        types = schema.get("types", [])
        type_count = len(types)
        for t in types:
            fields = t.get("fields") or []
            field_count += len(fields)
    except (ValueError, AttributeError, KeyError):
        # Response contained __schema text but couldn't parse details
        pass

    return Finding(
        id="GQL-001",
        module="graphql_introspection",
        category="web_application",
        title=f"GraphQL-Schema \u00f6ffentlich einsehbar: {url} ({type_count} Typen)",
        description=(
            f"Das GraphQL-Schema ist \u00fcber Introspection \u00f6ffentlich abrufbar. "
            f"Es enth\u00e4lt {type_count} Typen mit {field_count} Feldern. "
            f"Angreifer k\u00f6nnen damit die gesamte API-Struktur analysieren und "
            f"gezielt Schwachstellen in der Gesch\u00e4ftslogik finden."
        ),
        severity=Severity.HIGH,
        evidence=(
            f"Introspection-Query an {url} erfolgreich \u2014 "
            f"{type_count} Typen, {field_count} Felder exponiert"
        ),
        nis2_paragraphs=["\u00a730 Abs. 2 Nr. 5"],
        remediation=(
            "GraphQL-Introspection in der Produktionsumgebung deaktivieren. "
            "Bei Apollo Server: introspection: false. Bei anderen Frameworks: "
            "entsprechende Konfigurationsoption setzen."
        ),
    )


@register
class GraphqlIntrospectionModule(BaseModule):
    name = "graphql_introspection"
    description = "GraphQL Introspection Exposure"
    phase = 5
    step = 9

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_graphql_introspection(f"https://{domain}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.graphql_introspection <domain>")
        sys.exit(1)

    target = sys.argv[1]
    if not target.startswith("http"):
        target = f"https://{target}"
    print(f"Checking GraphQL introspection for {target}...")
    findings = check_graphql_introspection(target)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
