"""M30: JavaScript Source Map Exposure.

Usage: python -m argus.modules.source_maps https://true-fruits.com
"""

from __future__ import annotations

import logging
import re

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.source_maps")


def check_source_maps(base_url: str) -> list[Finding]:
    """Check if JS source maps are publicly accessible."""
    findings: list[Finding] = []

    try:
        resp = requests.get(base_url, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            return findings
    except requests.RequestException:
        return findings

    # Find JS files referenced in the page
    js_files = re.findall(r'src=["\']([^"\']*\.js)[^"\']*["\']', resp.text)

    checked = 0
    for js_file in js_files[:15]:  # Cap to avoid excessive requests
        # Build absolute URL for the .map file
        if js_file.startswith("//"):
            map_url = f"https:{js_file}.map"
        elif js_file.startswith("http"):
            map_url = f"{js_file}.map"
        elif js_file.startswith("/"):
            map_url = f"{base_url}{js_file}.map"
        else:
            map_url = f"{base_url}/{js_file}.map"

        try:
            map_resp = requests.head(map_url, timeout=5, allow_redirects=True)
            if map_resp.status_code == 200:
                content_length = int(map_resp.headers.get("Content-Length", 0))
                if content_length > 1000:  # Real source map, not error page
                    findings.append(Finding(
                        id="SRCMAP-001",
                        module="source_maps",
                        category="web_application",
                        title="JavaScript Source Map öffentlich zugänglich",
                        description=(
                            "Source Maps enthalten den originalen, nicht-minifizierten "
                            "Quellcode der Anwendung — inklusive Kommentare, Variablennamen "
                            "und Geschäftslogik. Ein Angreifer kann damit Schwachstellen "
                            "im Code finden."
                        ),
                        severity=Severity.HIGH,
                        evidence=(
                            f"HEAD {map_url} → HTTP 200, "
                            f"{content_length} Bytes (enthält Original-Quellcode)"
                        ),
                        nis2_paragraphs=["§30 Abs. 2 Nr. 5"],
                        remediation="Source Maps nicht auf Production-Servern deployen oder Zugriff blockieren.",
                    ))
                    return findings  # One source map is enough proof
            checked += 1
        except requests.RequestException:
            continue

    return findings


@register
class SourceMapsModule(BaseModule):
    name = "source_maps"
    description = "JavaScript Source Map Exposure"
    phase = 2
    step = 2

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return check_source_maps(f"https://{domain}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.source_maps <url>")
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith("http"):
        url = f"https://{url}"
    print(f"Checking source maps for {url}...")
    findings = check_source_maps(url)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    print(f"\n{len(findings)} findings")
