"""M12: Credential Exposure (HIBP) — checks employee emails against Have I Been Pwned.

Usage: python -m argus.modules.credential_exposure <domain>
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.credential_exposure")

# Common German business email patterns
COMMON_PREFIXES = ["info", "kontakt", "bewerbung", "datenschutz"]

NIS2_REF = "§30 Abs. 2 Nr. 7"

HIBP_BASE_URL = "https://haveibeenpwned.com/api/v3/breachedaccount"
HIBP_USER_AGENT = "KENGO-ARGUS-Scanner"
HIBP_RATE_LIMIT_SLEEP = 1.6  # HIBP enforces 1.5s minimum between requests

# Data classes that indicate password exposure
PASSWORD_DATA_CLASSES = {"Passwords", "Password hints", "Security questions and answers"}
FINANCIAL_DATA_CLASSES = {"Credit cards", "Bank account numbers", "Credit card CVV"}


def _collect_emails(domain: str, context: ScanContext) -> list[str]:
    """Collect and deduplicate emails to check."""
    emails: set[str] = set()

    if context.gf_email:
        emails.add(context.gf_email.lower().strip())

    for email in context.employee_emails:
        emails.add(email.lower().strip())

    for prefix in COMMON_PREFIXES:
        emails.add(f"{prefix}@{domain}")

    return sorted(emails)


def _is_recent_breach(breach_date_str: str) -> bool:
    """Check if a breach is less than 2 years old."""
    try:
        breach_date = datetime.strptime(breach_date_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        now = datetime.now(timezone.utc)
        delta = now - breach_date
        return delta.days < (365 * 2)
    except (ValueError, TypeError):
        return False


def _breach_year(breach_date_str: str) -> str:
    """Extract year from breach date string."""
    try:
        return breach_date_str[:4]
    except (TypeError, IndexError):
        return "unbekannt"


def _has_password_data(data_classes: list[str]) -> bool:
    """Check if breach contains password-related data."""
    return bool(PASSWORD_DATA_CLASSES & set(data_classes))


def _query_hibp(email: str, api_key: str) -> list[dict] | None:
    """Query HIBP for a single email. Returns breach list, empty list, or None on error."""
    url = f"{HIBP_BASE_URL}/{email}?truncateResponse=false"
    headers = {
        "hibp-api-key": api_key,
        "User-Agent": HIBP_USER_AGENT,
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            # Not found — email is clean
            return []
        if resp.status_code == 429:
            # Rate limited — wait and retry once
            retry_after = int(resp.headers.get("Retry-After", "2"))
            logger.warning(
                "HIBP Rate-Limit erreicht für %s — warte %ds und versuche erneut",
                email,
                retry_after,
            )
            time.sleep(retry_after)
            resp2 = requests.get(url, headers=headers, timeout=10)
            if resp2.status_code == 200:
                return resp2.json()
            if resp2.status_code == 404:
                return []
            logger.warning(
                "HIBP Retry fehlgeschlagen für %s: HTTP %d", email, resp2.status_code
            )
            return None

        logger.warning("HIBP-Abfrage fehlgeschlagen für %s: HTTP %d", email, resp.status_code)
        return None

    except requests.RequestException as e:
        logger.warning("HIBP-Anfrage fehlgeschlagen für %s: %s", email, e)
        return None


def scan_credential_exposure(
    domain: str, context: ScanContext
) -> list[Finding]:
    """Check collected emails against HIBP and generate findings."""
    findings: list[Finding] = []

    if not settings.hibp_api_key:
        logger.info("Kein HIBP-API-Key konfiguriert — Modul wird übersprungen")
        return findings

    emails = _collect_emails(domain, context)
    if not emails:
        logger.info("Keine E-Mail-Adressen zum Prüfen vorhanden")
        return findings

    logger.info("HIBP-Prüfung für %d E-Mail-Adresse(n)", len(emails))

    gf_email_lower = context.gf_email.lower().strip() if context.gf_email else None

    # Track breaches per email for CRED-005
    breaches_per_email: defaultdict[str, list[dict]] = defaultdict(list)

    for idx, email in enumerate(emails):
        if idx > 0:
            time.sleep(HIBP_RATE_LIMIT_SLEEP)

        breaches = _query_hibp(email, settings.hibp_api_key)
        if breaches is None:
            # API error — skip this email
            continue
        if not breaches:
            logger.debug("HIBP: %s — keine Datenlecks gefunden", email)
            continue

        logger.info("HIBP: %s — %d Datenleck(s) gefunden", email, len(breaches))
        breaches_per_email[email] = breaches

        is_gf = gf_email_lower is not None and email == gf_email_lower

        for breach in breaches:
            breach_name = breach.get("Name", "Unbekannt")
            breach_date = breach.get("BreachDate", "")
            data_classes = breach.get("DataClasses", [])
            year = _breach_year(breach_date)
            recent = _is_recent_breach(breach_date)
            has_passwords = _has_password_data(data_classes)

            data_classes_str = ", ".join(data_classes) if data_classes else "unbekannt"
            evidence_base = (
                f"HIBP API breachedaccount/{email} → "
                f"Breach: {breach_name}, Datum: {breach_date}, "
                f"Datenklassen: {data_classes_str}"
            )

            # CRED-004: GF/CEO email in any breach (takes priority)
            if is_gf:
                findings.append(
                    Finding(
                        id="CRED-004",
                        module="credential_exposure",
                        category="credential_exposure",
                        title=f"Geschäftsführer-E-Mail in Datenleck: {breach_name}",
                        description=(
                            f"Die E-Mail-Adresse des Geschäftsführers ({email}) wurde "
                            f"im Datenleck '{breach_name}' ({year}) gefunden. "
                            f"Kompromittierte Geschäftsführer-Konten stellen ein "
                            f"erhebliches Risiko für CEO-Fraud und Spear-Phishing dar."
                        ),
                        severity=Severity.CRITICAL,
                        evidence=evidence_base,
                        nis2_paragraphs=[NIS2_REF],
                        remediation=(
                            "Alle Passwörter des Geschäftsführers sofort ändern. "
                            "Multi-Faktor-Authentifizierung für alle Konten aktivieren. "
                            "Geschäftsführung für CEO-Fraud-Angriffe sensibilisieren."
                        ),
                    )
                )
                continue

            # CRED-001: Breach containing passwords
            if has_passwords:
                findings.append(
                    Finding(
                        id="CRED-001",
                        module="credential_exposure",
                        category="credential_exposure",
                        title=f"Passwort-Exposure: {email} in {breach_name}",
                        description=(
                            f"Die E-Mail-Adresse {email} wurde im Datenleck "
                            f"'{breach_name}' ({year}) gefunden. Dieses Leck enthält "
                            f"Passwörter, die für Credential-Stuffing-Angriffe "
                            f"missbraucht werden können."
                        ),
                        severity=Severity.CRITICAL,
                        evidence=evidence_base,
                        nis2_paragraphs=[NIS2_REF],
                        remediation=(
                            f"Passwort für {email} sofort ändern. Prüfen, ob dasselbe "
                            f"Passwort für weitere Konten verwendet wird (Password Reuse). "
                            f"Multi-Faktor-Authentifizierung aktivieren."
                        ),
                    )
                )
            elif recent:
                # CRED-002: Recent breach (< 2 years)
                findings.append(
                    Finding(
                        id="CRED-002",
                        module="credential_exposure",
                        category="credential_exposure",
                        title=f"{email} in aktuellem Datenleck: {breach_name} ({year})",
                        description=(
                            f"Die E-Mail-Adresse {email} wurde im aktuellen Datenleck "
                            f"'{breach_name}' ({year}) gefunden. Betroffene Datenklassen: "
                            f"{data_classes_str}. Aktuelle Datenlecks stellen ein erhöhtes "
                            f"Risiko dar, da die Daten noch aktiv gehandelt werden."
                        ),
                        severity=Severity.HIGH,
                        evidence=evidence_base,
                        nis2_paragraphs=[NIS2_REF],
                        remediation=(
                            f"Passwort für {email} ändern und auf verdächtige Aktivitäten "
                            f"überwachen. Multi-Faktor-Authentifizierung aktivieren."
                        ),
                    )
                )
            else:
                # CRED-003: Older breach
                findings.append(
                    Finding(
                        id="CRED-003",
                        module="credential_exposure",
                        category="credential_exposure",
                        title=f"{email} in Datenleck: {breach_name} ({year})",
                        description=(
                            f"Die E-Mail-Adresse {email} wurde im Datenleck "
                            f"'{breach_name}' ({year}) gefunden. Betroffene Datenklassen: "
                            f"{data_classes_str}. Auch ältere Datenlecks können ein Risiko "
                            f"darstellen, wenn Passwörter wiederverwendet werden."
                        ),
                        severity=Severity.MEDIUM,
                        evidence=evidence_base,
                        nis2_paragraphs=[NIS2_REF],
                        remediation=(
                            f"Prüfen, ob das Passwort für {email} seit {year} geändert "
                            f"wurde. Passwort-Richtlinien durchsetzen und "
                            f"Multi-Faktor-Authentifizierung aktivieren."
                        ),
                    )
                )

    # CRED-005: Same email in 3+ breaches
    for email, breaches in breaches_per_email.items():
        if len(breaches) >= 3:
            breach_names = [b.get("Name", "?") for b in breaches]
            findings.append(
                Finding(
                    id="CRED-005",
                    module="credential_exposure",
                    category="credential_exposure",
                    title=f"{email} in {len(breaches)} Datenlecks gefunden",
                    description=(
                        f"Die E-Mail-Adresse {email} wurde in {len(breaches)} "
                        f"verschiedenen Datenlecks gefunden: "
                        f"{', '.join(breach_names)}. "
                        f"Häufiges Auftreten in Datenlecks deutet auf mangelnde "
                        f"Passwort-Hygiene und erhöhtes Risiko für "
                        f"Credential-Stuffing-Angriffe hin."
                    ),
                    severity=Severity.HIGH,
                    evidence=(
                        f"HIBP API breachedaccount/{email} → "
                        f"{len(breaches)} Breaches: {', '.join(breach_names)}"
                    ),
                    nis2_paragraphs=[NIS2_REF],
                    remediation=(
                        f"Alle Passwörter für {email} ändern. Einen Passwort-Manager "
                        f"einführen und eindeutige Passwörter für jeden Dienst verwenden. "
                        f"Multi-Faktor-Authentifizierung für alle Konten aktivieren."
                    ),
                )
            )

    logger.info(
        "HIBP-Prüfung abgeschlossen: %d E-Mail(s), %d Finding(s)",
        len(emails),
        len(findings),
    )

    return findings


@register
class CredentialExposureModule(BaseModule):
    name = "credential_exposure"
    description = "Credential Exposure (HIBP)"
    phase = 4
    step = 6

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return scan_credential_exposure(domain, context)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.credential_exposure <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"HIBP Credential-Exposure-Check für {domain}...")

    ctx = ScanContext(domain=domain)

    # Optionally accept GF email via CLI
    if len(sys.argv) >= 3:
        ctx.gf_email = sys.argv[2]
        print(f"GF-E-Mail: {ctx.gf_email}")

    findings = scan_credential_exposure(domain, ctx)

    print(f"\n{'='*60}")
    print(f"HIBP-Ergebnisse für {domain}")
    print(f"{'='*60}")
    print(f"Geprüfte E-Mails: {', '.join(_collect_emails(domain, ctx))}")
    print(f"\nFindings ({len(findings)}):")
    print(f"{'='*60}")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()
