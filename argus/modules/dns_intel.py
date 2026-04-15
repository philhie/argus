"""M01: DNS Intelligence — SPF/DMARC/DKIM/MTA-STS/DANE/BIMI analysis.

Usage: python -m argus.modules.dns_intel true-fruits.com
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import dns.resolver

from argus.models import ARecord, DNSResult, Finding, MXRecord, ScanContext, Severity
from argus.modules import register
from argus.modules.base import BaseModule

logger = logging.getLogger("argus.dns_intel")

DKIM_SELECTORS = [
    "default", "selector1", "selector2", "google", "mail",
    "k1", "k2", "k3", "s1", "s2", "dkim", "mandrill",
    "mailjet", "cm", "mxvault", "exchange", "ex1", "ex2",
    # German ESPs
    "brevo", "rapidmail", "cleverreach", "newsletter",
    "sendinblue", "mailgun", "postmark",
]

# Known mail providers by MX hostname patterns
MAIL_PROVIDERS = {
    "google.com": "google",
    "googlemail.com": "google",
    "outlook.com": "exchange_online",
    "protection.outlook.com": "exchange_online",
    "pphosted.com": "proofpoint",
    "mimecast.com": "mimecast",
    "barracuda": "barracuda",
}

# Known NS providers
NS_PROVIDERS = {
    "cloudflare": "Cloudflare",
    "awsdns": "AWS Route53",
    "azure-dns": "Azure DNS",
    "hetzner": "Hetzner",
    "ionos": "IONOS",
    "strato": "Strato",
    "hosteurope": "Host Europe",
    "inwx": "INWX",
    "domaincontrol": "GoDaddy",
    "registrar-servers": "Namecheap",
}


def _resolve(qname: str, rdtype: str, resolver: dns.resolver.Resolver) -> list:
    """Safe DNS resolve wrapper."""
    try:
        return list(resolver.resolve(qname, rdtype))
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers, dns.exception.Timeout,
            dns.resolver.LifetimeTimeout):
        return []
    except Exception as e:
        logger.debug(f"DNS query {rdtype} {qname} failed: {e}")
        return []


def _classify_mail_server(mx_host: str) -> str:
    """Classify MX host into provider category."""
    mx_lower = mx_host.lower()
    for pattern, provider in MAIL_PROVIDERS.items():
        if pattern in mx_lower:
            return provider
    return "other"


def _identify_ns_provider(ns_records: list[str]) -> Optional[str]:
    """Identify DNS provider from nameserver hostnames."""
    for ns in ns_records:
        ns_lower = ns.lower()
        for pattern, provider in NS_PROVIDERS.items():
            if pattern in ns_lower:
                return provider
    return None


def _extract_spf_mechanism(spf: str) -> Optional[str]:
    """Extract the all-mechanism from SPF record."""
    match = re.search(r'([~?+\-])all', spf)
    if match:
        return f"{match.group(1)}all"
    if spf.strip().endswith("all"):
        return "all"
    return None


def _extract_dmarc_tag(record: str, tag: str) -> Optional[str]:
    """Extract a specific tag value from DMARC record."""
    match = re.search(rf'{tag}\s*=\s*([^;\s]+)', record)
    return match.group(1) if match else None


def _count_spf_lookups(spf: str) -> int:
    """Count DNS lookups in SPF record (include, a, mx, redirect, exists)."""
    count = 0
    count += len(re.findall(r'include:', spf))
    count += len(re.findall(r'\ba\b', spf))  # 'a' mechanism
    count += len(re.findall(r'\bmx\b', spf))  # 'mx' mechanism
    count += len(re.findall(r'redirect=', spf))
    count += len(re.findall(r'exists:', spf))
    return count


def _resolve_ip(hostname: str, resolver: dns.resolver.Resolver) -> Optional[str]:
    """Resolve hostname to IP."""
    answers = _resolve(hostname, 'A', resolver)
    return str(answers[0]) if answers else None


def scan_dns(domain: str) -> tuple[DNSResult, list[Finding]]:
    """Full DNS intelligence scan. Returns raw data + findings."""
    result = DNSResult()
    findings: list[Finding] = []
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    resolver.timeout = 5
    resolver.lifetime = 10

    # --- A Records ---
    for answer in _resolve(domain, 'A', resolver):
        result.a_records.append(ARecord(ip=str(answer)))

    # --- MX Records ---
    for answer in _resolve(domain, 'MX', resolver):
        mx_host = str(answer.exchange).rstrip('.')
        mx_ip = _resolve_ip(mx_host, resolver)
        result.mx_records.append(MXRecord(
            priority=answer.preference,
            host=mx_host,
            ip=mx_ip,
            mail_type=_classify_mail_server(mx_host),
        ))

    # --- All TXT Records ---
    for answer in _resolve(domain, 'TXT', resolver):
        txt = str(answer).strip('"')
        result.txt_records.append(txt)

    # --- SPF ---
    for txt in result.txt_records:
        if txt.startswith('v=spf1'):
            result.spf_record = txt
            result.spf_mechanism = _extract_spf_mechanism(txt)
            result.spf_includes = re.findall(r'include:(\S+)', txt)
            result.spf_ips = re.findall(r'ip[46]:(\S+)', txt)
            result.spf_lookup_count = _count_spf_lookups(txt)
            break

    # SPF Findings
    if result.spf_record is None:
        findings.append(Finding(
            id="DNS-002",
            module="dns_intel",
            category="email_security",
            title="Kein SPF-Record konfiguriert",
            description=(
                "Für die Domain existiert kein SPF-Record. Ohne SPF kann jeder "
                "Server im Internet E-Mails im Namen dieser Domain versenden. "
                "Dies ermöglicht Phishing-Angriffe gegen Mitarbeiter und Kunden."
            ),
            severity=Severity.CRITICAL,
            evidence=f"dig TXT {domain} → Kein Record mit 'v=spf1' gefunden",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation=(
                "SPF-Record als TXT-Record anlegen: v=spf1 include:<mailserver> -all. "
                "Wichtig: '-all' (hardfail) statt '~all' (softfail) verwenden."
            ),
        ))
    elif result.spf_mechanism in ("~all", "?all"):
        findings.append(Finding(
            id="DNS-001",
            module="dns_intel",
            category="email_security",
            title=f"SPF-Record mit schwachem Mechanismus ({result.spf_mechanism})",
            description=(
                f"Der SPF-Record endet mit '{result.spf_mechanism}' statt '-all'. "
                f"Dies bedeutet, dass nicht autorisierte Server E-Mails senden können "
                f"und diese nur als verdächtig markiert, aber nicht abgelehnt werden."
            ),
            severity=Severity.HIGH,
            evidence=f"dig TXT {domain} → {result.spf_record}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation=f"SPF-Mechanismus von '{result.spf_mechanism}' auf '-all' ändern.",
        ))

    if result.spf_lookup_count > 10:
        findings.append(Finding(
            id="DNS-010",
            module="dns_intel",
            category="email_security",
            title=f"SPF-Record überschreitet 10-Lookup-Limit ({result.spf_lookup_count} Lookups)",
            description=(
                "RFC 7208 erlaubt maximal 10 DNS-Lookups in einem SPF-Record. "
                "Bei Überschreitung liefert die SPF-Prüfung 'PermError' und E-Mails "
                "können abgelehnt werden."
            ),
            severity=Severity.MEDIUM,
            evidence=f"SPF: {result.spf_record} → {result.spf_lookup_count} Lookups (Limit: 10)",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation="SPF-Record vereinfachen: includes reduzieren, IP-Bereiche zusammenfassen.",
        ))

    # --- DMARC ---
    for answer in _resolve(f"_dmarc.{domain}", 'TXT', resolver):
        txt = str(answer).strip('"')
        if 'v=DMARC1' in txt:
            result.dmarc_record = txt
            result.dmarc_policy = _extract_dmarc_tag(txt, 'p')
            result.dmarc_subdomain_policy = _extract_dmarc_tag(txt, 'sp')
            result.dmarc_alignment_dkim = _extract_dmarc_tag(txt, 'adkim')
            result.dmarc_alignment_spf = _extract_dmarc_tag(txt, 'aspf')
            break

    if result.dmarc_record is None:
        findings.append(Finding(
            id="DNS-006",
            module="dns_intel",
            category="email_security",
            title="Kein DMARC-Record konfiguriert",
            description=(
                "Ohne DMARC-Record gibt es keine Richtlinie, wie empfangende Server "
                "mit E-Mails umgehen sollen, die SPF- oder DKIM-Prüfungen nicht bestehen. "
                "E-Mail-Spoofing wird dadurch deutlich erleichtert."
            ),
            severity=Severity.CRITICAL,
            evidence=f"dig TXT _dmarc.{domain} → Kein DMARC-Record gefunden",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation=(
                "DMARC-Record anlegen: _dmarc.{domain} TXT \"v=DMARC1; p=quarantine; "
                "rua=mailto:dmarc@{domain}\". Langfristig auf p=reject umstellen."
            ),
        ))
    elif result.dmarc_policy == "none":
        findings.append(Finding(
            id="DNS-004",
            module="dns_intel",
            category="email_security",
            title="DMARC-Policy auf 'none' — kein Schutz aktiv",
            description=(
                "Die DMARC-Policy 'none' bedeutet, dass empfangende Server keine "
                "Maßnahmen gegen gefälschte E-Mails ergreifen. DMARC existiert nur "
                "im Monitoring-Modus und bietet keinen aktiven Schutz."
            ),
            severity=Severity.HIGH,
            evidence=f"dig TXT _dmarc.{domain} → {result.dmarc_record}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation="DMARC-Policy von 'none' auf 'quarantine' oder 'reject' umstellen.",
        ))

    # Check subdomain policy gap
    if (result.dmarc_policy and result.dmarc_policy != "none"
            and result.dmarc_subdomain_policy == "none"):
        findings.append(Finding(
            id="DNS-005",
            module="dns_intel",
            category="email_security",
            title="DMARC Subdomain-Policy auf 'none' — Subdomain-Spoofing möglich",
            description=(
                f"Die Haupt-Policy ist '{result.dmarc_policy}', aber die Subdomain-Policy "
                f"(sp=none) erlaubt weiterhin Spoofing von Subdomains wie "
                f"mail.{domain} oder intern.{domain}."
            ),
            severity=Severity.HIGH,
            evidence=f"DMARC: p={result.dmarc_policy}, sp={result.dmarc_subdomain_policy}",
            nis2_paragraphs=["§30 Abs. 2 Nr. 2"],
            remediation="sp=none aus dem DMARC-Record entfernen oder auf sp=quarantine setzen.",
        ))

    # --- DKIM ---
    for selector in DKIM_SELECTORS:
        result.dkim_selectors_checked.append(selector)
        answers = _resolve(f"{selector}._domainkey.{domain}", 'TXT', resolver)
        if answers:
            result.dkim_selectors_found.append(selector)

    if not result.dkim_selectors_found:
        checked_str = ", ".join(result.dkim_selectors_checked)
        findings.append(Finding(
            id="DNS-003",
            module="dns_intel",
            category="email_security",
            title="Kein DKIM unter getesteten Selektoren gefunden",
            description=(
                f"Keiner der {len(DKIM_SELECTORS)} getesteten DKIM-Selektoren hat "
                f"einen gültigen Record. Ohne DKIM können E-Mails nicht kryptografisch "
                f"verifiziert werden und DMARC-Alignment schlägt fehl. "
                f"Hinweis: Es ist möglich, dass ein nicht-standardmäßiger Selektor verwendet wird."
            ),
            severity=Severity.HIGH,
            evidence=(
                f"Getestete Selektoren: {checked_str} — "
                f"alle ohne DKIM-Record ({len(DKIM_SELECTORS)} Selektoren geprüft)"
            ),
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation="DKIM bei Ihrem E-Mail-Provider aktivieren und DNS-Records publizieren.",
        ))

    # --- MTA-STS ---
    answers = _resolve(f"_mta-sts.{domain}", 'TXT', resolver)
    result.mta_sts = bool(answers)
    if not result.mta_sts:
        findings.append(Finding(
            id="DNS-007",
            module="dns_intel",
            category="email_security",
            title="Kein MTA-STS konfiguriert",
            description=(
                "Ohne MTA-STS können E-Mails über unverschlüsselte Verbindungen "
                "zugestellt werden, selbst wenn der Mailserver TLS unterstützt "
                "(Downgrade-Angriff)."
            ),
            severity=Severity.MEDIUM,
            evidence=f"dig TXT _mta-sts.{domain} → Kein Record gefunden",
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation="MTA-STS-Policy einrichten und _mta-sts TXT-Record publizieren.",
        ))

    # --- DANE/TLSA ---
    for mx in result.mx_records:
        answers = _resolve(f"_25._tcp.{mx.host}", 'TLSA', resolver)
        if answers:
            result.dane_tlsa = True
            break
    if not result.dane_tlsa and result.mx_records:
        findings.append(Finding(
            id="DNS-008",
            module="dns_intel",
            category="email_security",
            title="Kein DANE/TLSA für Mailserver konfiguriert",
            description=(
                "DANE/TLSA bindet das TLS-Zertifikat des Mailservers an DNS. "
                "Ohne DANE können Man-in-the-Middle-Angriffe auf die "
                "E-Mail-Zustellung nicht verhindert werden."
            ),
            severity=Severity.MEDIUM,
            evidence=(
                "Getestet: " +
                ", ".join(f"_25._tcp.{mx.host}" for mx in result.mx_records) +
                " → Keine TLSA-Records gefunden"
            ),
            nis2_paragraphs=["§30 Abs. 2 Nr. 8"],
            remediation="DANE/TLSA-Records für alle MX-Server einrichten (erfordert DNSSEC).",
        ))

    # --- BIMI ---
    answers = _resolve(f"default._bimi.{domain}", 'TXT', resolver)
    result.bimi = bool(answers)
    if not result.bimi:
        findings.append(Finding(
            id="DNS-009",
            module="dns_intel",
            category="email_security",
            title="Kein BIMI-Record konfiguriert",
            description=(
                "BIMI (Brand Indicators for Message Identification) zeigt das "
                "Firmenlogo in E-Mail-Clients an und erhöht die E-Mail-Authentizität. "
                "Voraussetzung ist eine DMARC-Policy von 'quarantine' oder 'reject'."
            ),
            severity=Severity.LOW,
            evidence=f"dig TXT default._bimi.{domain} → Kein Record gefunden",
            nis2_paragraphs=[],
            remediation="BIMI-Record einrichten und SVG-Logo bereitstellen (erfordert DMARC p=quarantine/reject).",
        ))

    # --- NS Records ---
    for answer in _resolve(domain, 'NS', resolver):
        result.ns_records.append(str(answer).rstrip('.'))
    result.ns_provider = _identify_ns_provider(result.ns_records)

    return result, findings


@register
class DnsIntelModule(BaseModule):
    name = "dns_intel"
    description = "DNS Intelligence — SPF/DMARC/DKIM/MTA-STS/DANE/BIMI"
    phase = 1
    step = 1

    def scan(self, domain: str, context: ScanContext) -> list[Finding]:
        dns_result, findings = scan_dns(domain)

        # Populate context
        context.dns = dns_result
        for a in dns_result.a_records:
            context.discovered_ips.add(a.ip)
        for mx in dns_result.mx_records:
            context.mx_hosts.append(mx.host)
            if mx.ip:
                context.discovered_ips.add(mx.ip)

        return findings


# Standalone execution
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m argus.modules.dns_intel <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"Scanning DNS for {domain}...")
    dns_result, findings = scan_dns(domain)

    print(f"\n{'='*60}")
    print(f"DNS Results for {domain}")
    print(f"{'='*60}")
    print(json.dumps(dns_result.model_dump(), indent=2, default=str))

    print(f"\n{'='*60}")
    print(f"Findings ({len(findings)})")
    print(f"{'='*60}")
    for f in findings:
        print(f"  [{f.severity.value}] {f.id}: {f.title}")
        print(f"    Evidence: {f.evidence[:120]}")
        print()
