"""M17: LLM Attack Path Narrative.

Uses Claude API to generate a German attack narrative from scan findings.

Usage: python -m argus.modules.attack_path example.com
"""

from __future__ import annotations

import logging

from argus.config import settings
from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.attack_path")

SYSTEM_PROMPT = (
    "Du bist ein erfahrener Penetration-Tester und schreibst einen realistischen "
    "Angriffsnarrativ für einen OSINT-Bericht. Beschreibe in 3-5 Absätzen, wie ein "
    "Angreifer die gefundenen Schwachstellen ausnutzen könnte. Beginne mit dem "
    "wahrscheinlichsten Einstiegspunkt und beschreibe laterale Bewegung. "
    "Quantifiziere potentiellen Schaden. Schreibe auf Deutsch, sachlich und "
    "professionell."
)

# Severity ordering for prompt grouping (most severe first)
_SEVERITY_ORDER = [
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.MEDIUM,
    Severity.LOW,
    Severity.INFO,
]

MAX_FINDINGS_IN_PROMPT = 50
MAX_EVIDENCE_LENGTH = 200


def _build_prompt(context: ScanContext) -> str:
    """Build a user prompt summarising findings and context for the LLM."""
    lines: list[str] = []

    # Context header
    lines.append(f"Domain: {context.domain}")
    if context.company_name:
        lines.append(f"Unternehmen: {context.company_name}")

    # Technologies
    if context.technologies:
        tech_names = [
            t.get("name", str(t)) for t in context.technologies[:20]
        ]
        lines.append(f"Technologien: {', '.join(tech_names)}")

    # MSP info
    if context.msp_info:
        msp_name = context.msp_info.get("name", "unbekannt")
        msp_confidence = context.msp_info.get("confidence", "")
        lines.append(f"IT-Dienstleister: {msp_name} (Konfidenz: {msp_confidence})")

    lines.append("")
    lines.append("=== Findings ===")

    # Group findings by severity
    findings_by_severity: dict[Severity, list[Finding]] = {}
    for f in context.findings:
        findings_by_severity.setdefault(f.severity, []).append(f)

    count = 0
    for severity in _SEVERITY_ORDER:
        group = findings_by_severity.get(severity, [])
        if not group:
            continue
        lines.append(f"\n--- {severity.value} ---")
        for f in group:
            if count >= MAX_FINDINGS_IN_PROMPT:
                lines.append(f"... ({len(context.findings) - count} weitere Findings gekürzt)")
                return "\n".join(lines)
            evidence = f.evidence[:MAX_EVIDENCE_LENGTH]
            if len(f.evidence) > MAX_EVIDENCE_LENGTH:
                evidence += "..."
            lines.append(f"[{f.id}] {f.title}")
            lines.append(f"  Evidenz: {evidence}")
            count += 1

    return "\n".join(lines)


def generate_attack_path(context: ScanContext) -> list[Finding]:
    """Call Claude API to generate an attack path narrative. Returns [] always."""
    if not settings.anthropic_api_key:
        logger.info("Kein Anthropic API-Key konfiguriert — Attack-Path-Modul übersprungen.")
        return []

    if not context.findings:
        logger.info("Keine Findings vorhanden — Attack-Path-Modul übersprungen.")
        return []

    try:
        import anthropic  # noqa: F811
    except ImportError:
        logger.info("anthropic-Paket nicht installiert — Attack-Path-Modul übersprungen.")
        return []

    prompt = _build_prompt(context)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        narrative = message.content[0].text
        context.attack_path_narrative = narrative
        logger.info(
            "Attack-Path-Narrativ generiert (%d Zeichen).", len(narrative)
        )
    except Exception:
        logger.warning("Fehler beim Aufruf der Claude API.", exc_info=True)

    return []


@register
class AttackPathModule(BaseModule):
    name = "attack_path"
    description = "LLM Attack Path Narrative"
    phase = 6
    step = 10

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return generate_attack_path(context)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.attack_path <domain>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"Attack path narrative for {target}...")
    print("Note: This module requires findings from prior scan phases.")

    # Demo with empty context
    ctx = ScanContext(domain=target)
    results = generate_attack_path(ctx)
    if ctx.attack_path_narrative:
        print(f"\nNarrative:\n{ctx.attack_path_narrative}")
    else:
        print("\nNo narrative generated (missing API key or findings).")
    print(f"\n{len(results)} findings (context enrichment only)")
