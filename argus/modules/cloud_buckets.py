"""M33: Cloud Bucket Discovery (S3/Azure/GCS) — enumerates bucket names and tests public access.

Usage: python -m argus.modules.cloud_buckets <domain> [company_name]
"""

from __future__ import annotations

import logging
import re

import requests

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.cloud_buckets")

NIS2_REF = "§30 Abs. 2 Nr. 1"

SUFFIXES = [
    "",
    "-backup",
    "-backups",
    "-dev",
    "-staging",
    "-prod",
    "-assets",
    "-media",
    "-uploads",
    "-data",
    "-logs",
    "-public",
    "-private",
    "-files",
    "-static",
]

# German corporate suffixes to strip from company name
CORP_SUFFIXES_RE = re.compile(
    r"\s*(gmbh|ag|kg|e\.v\.|ohg|gbr|ug|mbh|co\.kg|gmbh\s*&\s*co\.?\s*kg)\s*$",
    re.IGNORECASE,
)

REQUEST_TIMEOUT = 5


def _generate_candidates(domain: str, company_name: str) -> list[str]:
    """Generate bucket name candidates from domain and company name."""
    bases: set[str] = set()

    # domain with dots → hyphens  (e.g. "true-fruits.com" → "true-fruits-com")
    domain_hyphenated = domain.replace(".", "-").lower()
    bases.add(domain_hyphenated)

    # domain without TLD  (e.g. "true-fruits")
    parts = domain.lower().split(".")
    if len(parts) >= 2:
        without_tld = "-".join(parts[:-1])
        bases.add(without_tld)

    # company name: lowercase, spaces→hyphens, strip corporate suffixes
    if company_name:
        clean = CORP_SUFFIXES_RE.sub("", company_name).strip()
        clean = re.sub(r"\s+", "-", clean).lower()
        clean = re.sub(r"[^a-z0-9\-]", "", clean)
        if clean:
            bases.add(clean)

    candidates: list[str] = []
    seen: set[str] = set()
    for base in sorted(bases):
        for suffix in SUFFIXES:
            name = base + suffix
            if name and name not in seen:
                seen.add(name)
                candidates.append(name)

    return candidates


def _check_s3(name: str, session: requests.Session) -> dict | None:
    """Check S3 bucket. Returns dict with provider/status or None if not found."""
    url = f"https://{name}.s3.amazonaws.com"
    try:
        resp = session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            # Try GET to confirm publicly listable
            try:
                get_resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
                if get_resp.status_code == 200 and "<ListBucketResult" in get_resp.text:
                    return {"provider": "S3", "name": name, "status": "listable"}
            except requests.RequestException:
                pass
            # HEAD returned 200 but GET didn't confirm listable — treat as private
            return {"provider": "S3", "name": name, "status": "private"}
        if resp.status_code == 403:
            return {"provider": "S3", "name": name, "status": "private"}
    except requests.RequestException as exc:
        logger.debug("S3-Prüfung fehlgeschlagen für %s: %s", name, exc)
    return None


def _check_azure(name: str, session: requests.Session) -> dict | None:
    """Check Azure Blob Storage. Returns dict with provider/status or None."""
    url = f"https://{name}.blob.core.windows.net"
    try:
        resp = session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            return {"provider": "Azure Blob", "name": name, "status": "listable"}
        if resp.status_code in (403, 400):
            return {"provider": "Azure Blob", "name": name, "status": "private"}
    except requests.RequestException as exc:
        logger.debug("Azure-Prüfung fehlgeschlagen für %s: %s", name, exc)
    return None


def _check_gcs(name: str, session: requests.Session) -> dict | None:
    """Check Google Cloud Storage. Returns dict with provider/status or None."""
    url = f"https://storage.googleapis.com/{name}"
    try:
        resp = session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            return {"provider": "GCS", "name": name, "status": "listable"}
        if resp.status_code == 403:
            return {"provider": "GCS", "name": name, "status": "private"}
    except requests.RequestException as exc:
        logger.debug("GCS-Prüfung fehlgeschlagen für %s: %s", name, exc)
    return None


def scan_cloud_buckets(domain: str, context: ScanContext) -> list[Finding]:
    """Enumerate cloud bucket names and test public access."""
    findings: list[Finding] = []
    candidates = _generate_candidates(domain, context.company_name)

    if not candidates:
        logger.info("Keine Bucket-Kandidaten generiert für %s", domain)
        return findings

    logger.info(
        "Cloud-Bucket-Enumeration: %d Kandidaten für %s", len(candidates), domain
    )

    session = requests.Session()
    session.headers.update({"User-Agent": "KENGO-ARGUS-Scanner"})

    found_buckets: list[dict] = []

    for name in candidates:
        for checker in (_check_s3, _check_azure, _check_gcs):
            result = checker(name, session)
            if result is not None:
                found_buckets.append(result)

    # Generate findings
    for bucket in found_buckets:
        provider = bucket["provider"]
        name = bucket["name"]
        status = bucket["status"]

        if status == "listable":
            findings.append(
                Finding(
                    id="CLOUD-001",
                    module="cloud_buckets",
                    category="infrastructure",
                    title=f"Öffentlich lesbarer {provider}-Bucket: {name}",
                    description=(
                        f"Der Cloud-Bucket '{name}' bei {provider} ist öffentlich "
                        f"lesbar. Angreifer können alle darin gespeicherten Daten "
                        f"einsehen und herunterladen. Dies stellt ein erhebliches "
                        f"Datenschutz- und Sicherheitsrisiko dar."
                    ),
                    severity=Severity.CRITICAL,
                    evidence=f"HEAD/GET {provider} Bucket '{name}' → HTTP 200, öffentlich listbar",
                    nis2_paragraphs=[NIS2_REF],
                    remediation=(
                        f"Bucket '{name}' sofort auf privat umstellen. "
                        f"Alle gespeicherten Daten auf sensible Inhalte prüfen. "
                        f"Bucket-Policies und ACLs überprüfen und restriktiv konfigurieren."
                    ),
                )
            )
        elif status == "private":
            findings.append(
                Finding(
                    id="CLOUD-002",
                    module="cloud_buckets",
                    category="infrastructure",
                    title=f"Cloud-Bucket existiert (privat): {provider}/{name}",
                    description=(
                        f"Der Cloud-Bucket '{name}' bei {provider} existiert, ist aber "
                        f"nicht öffentlich zugänglich. Der Bucket-Name wurde anhand des "
                        f"Domainnamens erraten."
                    ),
                    severity=Severity.INFO,
                    evidence=f"HEAD {provider} Bucket '{name}' → HTTP 403 (existiert, privat)",
                    nis2_paragraphs=[NIS2_REF],
                    remediation=(
                        f"Bucket-Policies für '{name}' regelmäßig überprüfen. "
                        f"Sicherstellen, dass keine versehentliche Öffnung erfolgt."
                    ),
                )
            )

    # CLOUD-003: Many buckets found
    if len(found_buckets) > 3:
        company_label = context.company_name or domain
        bucket_list = ", ".join(
            f"{b['provider']}/{b['name']}" for b in found_buckets
        )
        findings.append(
            Finding(
                id="CLOUD-003",
                module="cloud_buckets",
                category="infrastructure",
                title=f"{len(found_buckets)} Cloud-Buckets für {company_label} identifiziert",
                description=(
                    f"Es wurden {len(found_buckets)} Cloud-Buckets identifiziert, "
                    f"die mit {company_label} in Verbindung stehen. Eine große Anzahl "
                    f"von Buckets erhöht die Angriffsfläche und erfordert "
                    f"systematisches Zugriffsmanagement."
                ),
                severity=Severity.MEDIUM,
                evidence=f"{len(found_buckets)} Buckets gefunden: {bucket_list}",
                nis2_paragraphs=[NIS2_REF],
                remediation=(
                    "Cloud-Storage-Inventar erstellen und regelmäßig auditieren. "
                    "Nicht benötigte Buckets entfernen. "
                    "Einheitliche Zugriffsrichtlinien durchsetzen."
                ),
            )
        )

    logger.info(
        "Cloud-Bucket-Enumeration abgeschlossen: %d Bucket(s), %d Finding(s)",
        len(found_buckets),
        len(findings),
    )

    return findings


@register
class CloudBucketsModule(BaseModule):
    name = "cloud_buckets"
    description = "Cloud Bucket Discovery (S3/Azure/GCS)"
    phase = 5
    step = 8

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_cloud_buckets(domain, context)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.cloud_buckets <domain> [company_name]")
        sys.exit(1)

    domain = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) >= 3 else ""

    print(f"Cloud-Bucket-Enumeration für {domain}...")
    if company_name:
        print(f"Firmenname: {company_name}")

    ctx = ScanContext(domain=domain, company_name=company_name)
    findings = scan_cloud_buckets(domain, ctx)

    print(f"\n{'='*60}")
    print(f"Cloud-Bucket-Ergebnisse für {domain}")
    print(f"{'='*60}")
    print(f"Kandidaten: {len(_generate_candidates(domain, company_name))}")
    print(f"\nFindings ({len(findings)}):")
    print(f"{'='*60}")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()
