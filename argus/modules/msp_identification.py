"""M13: Managed Service Provider Identification.

Usage: python -m argus.modules.msp_identification example.com
"""

from __future__ import annotations

import logging

from argus.models import Finding, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.msp_identification")

MSP_SIGNATURES: dict[str, list[str]] = {
    "DATEV": ["datev"],
    "Bechtle": ["bechtle"],
    "Cancom": ["cancom"],
    "T-Systems": ["t-systems", "telekom"],
    "All for One": ["all-for-one", "allforone"],
    "Arvato/Bertelsmann": ["arvato"],
    "Konica Minolta IT": ["konicaminolta"],
    "IONOS/1&1": ["ionos", "1and1", "1und1"],
    "Strato": ["strato"],
    "Hetzner": ["hetzner"],
    "OVH": ["ovh"],
    "HostEurope": ["hosteurope"],
    "Rackspace": ["rackspace"],
    "SysEleven": ["syseleven"],
    "noris network": ["noris"],
    "plusserver": ["plusserver"],
    "Claranet": ["claranet"],
    "q.beyond": ["qbeyond", "q-beyond"],
    "BREKOM": ["brekom"],
    "NetCologne": ["netcologne"],
}


def identify_msp(context: ScanContext) -> list[Finding]:
    """Cross-reference DNS records against known German IT provider signatures."""
    findings: list[Finding] = []

    # Collect all DNS strings to check
    dns_strings: list[tuple[str, str]] = []

    for ns in context.dns.ns_records:
        dns_strings.append((ns.lower(), "NS-Record"))

    for mx in context.dns.mx_records:
        dns_strings.append((mx.host.lower(), "MX-Record"))

    for spf_inc in context.dns.spf_includes:
        dns_strings.append((spf_inc.lower(), "SPF-Include"))

    for txt in context.dns.txt_records:
        dns_strings.append((txt.lower(), "TXT-Record"))

    if context.dns.ns_provider:
        dns_strings.append((context.dns.ns_provider.lower(), "NS-Provider"))

    # Match against MSP signatures
    matched_msps: dict[str, list[str]] = {}

    for msp_name, patterns in MSP_SIGNATURES.items():
        for dns_value, source in dns_strings:
            for pattern in patterns:
                if pattern in dns_value:
                    signal = f"{source}: {dns_value}"
                    matched_msps.setdefault(msp_name, []).append(signal)

    # Pick the MSP with the most signals (highest confidence)
    if not matched_msps:
        return findings

    best_msp = max(matched_msps, key=lambda k: len(matched_msps[k]))
    signals = matched_msps[best_msp]
    confidence = "hoch" if len(signals) >= 3 else "mittel" if len(signals) >= 2 else "niedrig"

    # Store in context for downstream modules
    context.msp_info = {
        "name": best_msp,
        "confidence": confidence,
        "signals": signals,
    }

    primary_signal = signals[0]
    findings.append(Finding(
        id="MSP-001",
        module="msp_identification",
        category="supply_chain",
        title=f"IT-Dienstleister identifiziert: {best_msp} (via {primary_signal})",
        description=(
            f"Der IT-Dienstleister '{best_msp}' wurde anhand von {len(signals)} "
            f"DNS-Signalen identifiziert (Konfidenz: {confidence}). "
            f"Lieferkettenrisiken sollten im Rahmen von NIS2 bewertet werden."
        ),
        severity=Severity.INFO,
        evidence=f"MSP '{best_msp}' erkannt via: {', '.join(signals)}",
        nis2_paragraphs=["\u00a730 Abs. 2 Nr. 4"],
        remediation=(
            "Sicherheitsanforderungen an IT-Dienstleister vertraglich festlegen "
            "(Auftragsverarbeitungsvertrag, SLA, Incident-Response-Pflichten). "
            "Regelm\u00e4\u00dfige \u00dcberpr\u00fcfung der Dienstleister-Sicherheit gem\u00e4\u00df NIS2."
        ),
    ))

    # Report additional MSPs if found
    for msp_name, msp_signals in matched_msps.items():
        if msp_name == best_msp:
            continue
        findings.append(Finding(
            id="MSP-002",
            module="msp_identification",
            category="supply_chain",
            title=f"IT-Dienstleister identifiziert: {msp_name} (via {msp_signals[0]})",
            description=(
                f"Weiterer IT-Dienstleister '{msp_name}' wurde anhand von "
                f"{len(msp_signals)} DNS-Signalen identifiziert."
            ),
            severity=Severity.INFO,
            evidence=f"MSP '{msp_name}' erkannt via: {', '.join(msp_signals)}",
            nis2_paragraphs=["\u00a730 Abs. 2 Nr. 4"],
            remediation=(
                "Sicherheitsanforderungen an IT-Dienstleister vertraglich festlegen."
            ),
        ))

    return findings


@register
class MspIdentificationModule(BaseModule):
    name = "msp_identification"
    description = "Managed Service Provider Identification"
    phase = 5
    step = 9

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        return identify_msp(context)


if __name__ == "__main__":
    import sys

    from argus.models import DNSResult, MXRecord

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.msp_identification <domain>")
        sys.exit(1)

    target = sys.argv[1]
    print(f"MSP identification for {target}...")
    print("Note: This module requires DNS data from prior scan phases.")

    # Demo with empty context
    ctx = ScanContext(domain=target, dns=DNSResult())
    findings = identify_msp(ctx)
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    {f.evidence}")
    if ctx.msp_info:
        print(f"\nMSP Info: {ctx.msp_info}")
    print(f"\n{len(findings)} findings")
