"""Stage 5 — translate a scanner finding into GF-language short/what copy.

Templates first (see templates.TEMPLATES). If no key matches we emit a
[REVIEW]-tagged fallback so QA can spot missing coverage — the pipeline
refuses to ship rows containing [REVIEW] in strict mode.
"""

from __future__ import annotations

import logging
import re
import string
from typing import Optional

from argus.export.templates import TEMPLATES

logger = logging.getLogger("argus")

REVIEW_TAG = "[REVIEW]"
MAX_SHORT_LENGTH = 50

_IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
_EMAIL_RE = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.IGNORECASE)
_PORT_RE = re.compile(r"Port\s+(\d+)", re.IGNORECASE)
_FIRST_INT_RE = re.compile(r"\d+")
_BREACH_COUNT_RE = re.compile(r"in (\d+)\s+(?:verschiedenen\s+)?Datenlecks")
_BYTES_RE = re.compile(r"(\d+)\s*Bytes")


class _EmptyFill(dict):
    """Formatter dict that returns '' for missing keys (no KeyError)."""

    def __missing__(self, key: str) -> str:  # pragma: no cover - trivial
        return ""


def build_template_key(finding: dict) -> Optional[str]:
    """Map a scanner finding to the template key it should render under."""
    module = finding.get("module", "") or ""
    title = finding.get("title", "") or ""
    fid = finding.get("id", "") or ""

    # ── Shodan / open services ────────────────────────────────────────
    if module == "shodan_lookup":
        if "MySQL" in title:
            return "shodan:mysql"
        if "FTP" in title:
            return "shodan:ftp"
        if "PostgreSQL" in title:
            return "shodan:postgresql"
        if "Redis" in title:
            return "shodan:redis"
        if "MongoDB" in title:
            return "shodan:mongodb"
        if "RDP" in title:
            return "shodan:rdp"
        if "SSH" in title:
            return "shodan:ssh"
        if "Telnet" in title:
            return "shodan:telnet"
        if "SMB" in title:
            return "shodan:smb"
        if "MSSQL" in title or "MS-SQL" in title:
            return "shodan:mssql"
        if "VNC" in title:
            return "shodan:vnc"
        if "Elasticsearch" in title:
            return "shodan:elasticsearch"
        if "Memcached" in title:
            return "shodan:memcached"
        if fid == "SHO-003" or "Betriebssystem" in title:
            return "shodan:outdated_os"
        if fid == "SHO-002" or fid == "SHO-002-AGG":
            return "shodan:cve"
        if fid == "SHO-004":
            return "shodan:many_ports"

    # ── Exchange ──────────────────────────────────────────────────────
    if module == "exchange":
        if fid in ("EX-003", "EX-004"):
            return "exchange:ecp_powershell"
        if fid == "EX-010":
            return "exchange:multiple_endpoints"
        if fid == "EX-005":
            return "exchange:basic_auth"
        if fid == "EX-001":
            return "exchange:eol"
        if fid == "EX-007":
            return "exchange:ad_domain_leak"
        if fid == "EX-008":
            return "exchange:fqdn_leak"
        if fid == "EX-009":
            return "exchange:hostname_leak"

    # ── File exposure (IDs are generated from path slug) ─────────────
    if module == "file_exposure":
        title_l = title.lower()
        if "web.config" in title_l:
            return "file:webconfig"
        if ".env" in title_l:
            return "file:env"
        if ".htpasswd" in title_l:
            return "file:htpasswd"
        if ".htaccess" in title_l:
            return "file:htaccess"
        if ".git" in title_l:
            return "file:git"
        if "composer.json" in title_l:
            return "file:composer"
        if "package.json" in title_l:
            return "file:package_json"
        if "phpinfo" in title_l:
            return "file:phpinfo"
        if "docker" in title_l:
            return "file:docker"
        if "backup" in title_l:
            return "file:backup"
        if "dump" in title_l:
            return "file:sqldump"

    # ── Email authentication ─────────────────────────────────────────
    if module == "dns_intel":
        if fid == "DNS-006":
            return "email:no_dmarc"
        if fid == "DNS-004":
            return "email:dmarc_none"
        if fid == "DNS-002":
            return "email:no_spf"
        if fid == "DNS-001":
            return "email:spf_weak"
        if fid == "DNS-003":
            return "email:no_dkim"
        if fid == "DNS-005":
            return "email:dmarc_subdomain_none"
        if fid == "DNS-007":
            return "email:no_mta_sts"
        if fid == "DNS-008":
            return "email:no_dane"
        if fid == "DNS-010":
            return "email:spf_too_many_lookups"

    # ── Zone transfer (own module) ────────────────────────────────────
    if module == "zone_transfer" or fid == "DNS-AXFR":
        return "email:zone_transfer"

    # ── Credentials / HIBP ────────────────────────────────────────────
    if module == "credential_exposure":
        if fid.startswith("CRED-004"):
            return "cred:hibp_gf"
        if fid.startswith("CRED-001"):
            return "cred:hibp_password"
        if fid.startswith("CRED-005"):
            return "cred:hibp_multiple"
        if fid.startswith("CRED-002"):
            return "cred:hibp_recent"
        if fid.startswith("CRED-003"):
            return "cred:hibp_metadata"

    # ── Admin panels ──────────────────────────────────────────────────
    if module == "admin_panel":
        if "phpMyAdmin" in title:
            return "admin:phpmyadmin"
        if "Adminer" in title:
            return "admin:adminer"
        if "cPanel" in title:
            return "admin:cpanel"
        if "Plesk" in title:
            return "admin:plesk"
        if "Webmail" in title:
            return "admin:webmail"
        if "WordPress" in title:
            return "admin:wordpress"
        if "TYPO3" in title:
            return "admin:typo3"
        if "Joomla" in title:
            return "admin:joomla"
        if "Drupal" in title:
            return "admin:drupal"
        # Generic fallback by panel type
        if fid.startswith("ADMIN-002"):
            return "admin:database_tool"
        if fid.startswith("ADMIN-003"):
            return "admin:server_management"
        return "admin:generic"

    # ── TLS ───────────────────────────────────────────────────────────
    if module == "tls_analysis":
        if "TLS 1.0" in title:
            return "tls:tls10"
        if "TLS 1.1" in title:
            return "tls:tls11"

    # ── Source maps ───────────────────────────────────────────────────
    if module == "source_maps":
        return "srcmap:exposed"

    # ── Google dorking ────────────────────────────────────────────────
    if module == "google_dorking":
        if "PDF" in title:
            return "dork:confidential_pdfs"
        if "Excel" in title:
            return "dork:excel"
        if "Admin" in title:
            return "dork:admin_indexed"
        if "CI/CD" in title or "CI-CD" in title:
            return "dork:cicd_indexed"
        if "Entwicklungstools" in title or "DevTools" in title:
            return "dork:devtools_indexed"

    # ── Subdomains ────────────────────────────────────────────────────
    if module == "subdomain_discovery":
        if fid == "SUB-004":
            return "sub:database"
        if fid == "SUB-002":
            return "sub:admin"
        if fid == "SUB-001":
            return "sub:staging"

    # ── Tech fingerprint ──────────────────────────────────────────────
    if module == "tech_fingerprint":
        if fid == "TECH-001":
            return "tech:outdated"
        if fid == "TECH-002":
            return "tech:version_leak"

    # ── Wayback Machine ───────────────────────────────────────────────
    if module == "wayback_machine":
        if fid == "WB-001":
            return "wayback:live_sensitive"
        if fid == "WB-002":
            return "wayback:archived_sensitive"
        if fid == "WB-003":
            return "wayback:many_sensitive"

    # ── HTTP headers (cookie issues) ──────────────────────────────────
    if module == "http_headers":
        if fid.startswith("HDR-COOKIE"):
            return "cookie:insecure"
        if fid == "HDR-002":
            return "header:missing_security"

    # ── CORS ────────────────────────────────────────────────────────────
    if module == "cors":
        if fid == "CORS-001":
            return "cors:wildcard"
        if fid == "CORS-002":
            return "cors:null_origin"
        if fid == "CORS-003":
            return "cors:credentials"

    # ── API discovery ──────────────────────────────────────────────────
    if module == "api_discovery":
        title_l = (title or "").lower()
        if "actuator" in title_l or "env" in title_l or "beans" in title_l:
            return "api:actuator_exposed"
        return "api:swagger_exposed"

    # ── Certificate issues ─────────────────────────────────────────────
    if module == "cert_san":
        if fid.startswith("CERT-002"):
            return "cert:self_signed"
        if fid.startswith("CERT-005"):
            return "cert:wrong_hostname"
        if fid.startswith("CERT-004"):
            return "cert:weak_key"
        if fid.startswith("CERT-001"):
            return "cert:expiring"

    # ── WHOIS ──────────────────────────────────────────────────────────
    if module == "whois_check" or fid == "WHOIS-001":
        return "whois:expiring"

    # ── Subdomain takeover ─────────────────────────────────────────────
    if module == "subdomain_takeover":
        return "takeover:dangling_cname"

    # ── DNSSEC ─────────────────────────────────────────────────────────
    if module == "dnssec" or fid == "DNSSEC-001":
        return "dnssec:not_enabled"

    # ── GraphQL ────────────────────────────────────────────────────────
    if module == "graphql_introspection" or fid == "GQL-001":
        return "graphql:introspection"

    # ── Favicon hash ───────────────────────────────────────────────────
    if module == "favicon_hash":
        return "favicon:known_product"

    # ── IP shared hosting ──────────────────────────────────────────────
    if fid == "IP-002":
        return "ip:shared_hosting"

    # ── Cloud buckets ─────────────────────────────────────────────────
    if module == "cloud_buckets":
        if fid == "CLOUD-001":
            return "cloud:public_bucket"

    # ── GitHub (post-filter only) ─────────────────────────────────────
    if module == "github_secrets":
        if "Privater Schlüssel" in title or "Private Key" in title:
            return "github:private_key"
        if "API-Key" in title or "API Key" in title:
            return "github:api_key"
        if "Datenbank-Credentials" in title or "DB-Credentials" in title:
            return "github:db_creds"
        if "AWS" in title:
            return "github:aws_key"
        if "Passwort" in title:
            return "github:password"

    return None


def _build_fills(finding: dict, scan_data: dict) -> dict:
    """Extract per-finding placeholder values from title/evidence."""
    evidence = finding.get("evidence", "") or ""
    title = finding.get("title", "") or ""
    domain = scan_data.get("domain", "") or ""

    fills: dict = {"domain": domain}

    ip_match = _IP_RE.search(evidence)
    if ip_match:
        fills["ip"] = ip_match.group(0)

    cves = finding.get("cve_ids", []) or []
    if cves:
        fills["cve_count"] = str(len(cves))
        fills["cve_example"] = cves[0]
    else:
        fills["cve_count"] = "mehrere"
        fills["cve_example"] = "CVE-XXXX-XXXX"

    count_match = _FIRST_INT_RE.search(title)
    fills["count"] = count_match.group(0) if count_match else "mehrere"

    bc_match = _BREACH_COUNT_RE.search(title)
    fills["breach_count"] = bc_match.group(1) if bc_match else "mehreren"

    # Count CRED-001 findings across the whole scan for pwd_count.
    pwd_findings = [
        f
        for f in (scan_data.get("findings", []) or [])
        if (f.get("id", "") or "").startswith("CRED-001")
    ]
    fills["pwd_count"] = str(len(pwd_findings)) if pwd_findings else "mehreren"

    port_match = _PORT_RE.search(evidence)
    fills["port"] = port_match.group(1) if port_match else ""

    bytes_match = _BYTES_RE.search(evidence)
    fills["bytes"] = bytes_match.group(1) if bytes_match else ""

    # Prefer an explicit email from title/evidence; fall back to info@domain.
    email_match = _EMAIL_RE.search(title) or _EMAIL_RE.search(evidence)
    if email_match:
        fills["email"] = email_match.group(0)
    elif domain:
        fills["email"] = f"info@{domain}"
    else:
        fills["email"] = ""

    # For tech:outdated use the part after the first colon in the title.
    if ":" in title:
        fills["version"] = title.split(":", 1)[1].strip()
    else:
        fills["version"] = title

    # Path from evidence (simple URL capture)
    path_match = re.search(r"(/[A-Za-z0-9/_.\-]+)", evidence)
    fills["path"] = path_match.group(1) if path_match else ""

    return fills


def _safe_format(tpl: str, fills: dict) -> str:
    """Format with empty-string fallback for missing keys.

    Unresolved placeholders would leak curly braces into the prospect's
    inbox. Empty-string fallback keeps the sentence well-formed; the
    strict-mode check downstream still fails loudly if the output string
    contains '{something}' — that catches literal-brace bugs in templates.
    """
    try:
        return string.Formatter().vformat(tpl, (), _EmptyFill(fills))
    except (ValueError, IndexError):
        return tpl


def translate_via_llm(finding: dict, scan_data: dict) -> Optional[dict]:
    """Hook point for Claude API fallback. v1: returns None.

    Wire here when template coverage drops. The contract is unchanged:
    return a dict with keys 'short' and 'what', or None to fall through.
    """
    return None


def translate_finding(finding: dict, scan_data: dict, use_llm: bool = False) -> dict:
    """Template lookup → LLM fallback → [REVIEW]-tagged safety net."""
    key = build_template_key(finding)
    if key and key in TEMPLATES:
        tpl = TEMPLATES[key]
        fills = _build_fills(finding, scan_data)
        short = _safe_format(tpl["short"], fills)
        what = _safe_format(tpl["what"], fills)
        if len(short) > MAX_SHORT_LENGTH:
            logger.warning(
                "Subject-line short exceeds %d chars (%d): %r — truncating",
                MAX_SHORT_LENGTH, len(short), short,
            )
            short = _truncate_at_word(short, MAX_SHORT_LENGTH)
        return {"short": short, "what": what}

    if use_llm:
        llm = translate_via_llm(finding, scan_data)
        if llm:
            return llm

    # Safety net: never crash, but flag loudly so QA can spot the gap.
    title = finding.get("title", "Unbekannte Schwachstelle") or "Unbekannte Schwachstelle"
    desc = finding.get("description") or title
    return {
        "short": _truncate_at_word(title, MAX_SHORT_LENGTH),
        "what": f"{REVIEW_TAG} {desc[:200]}",
    }


def _truncate_at_word(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    cut = s[:limit].rstrip()
    # Back up to the last space to avoid breaking mid-word.
    space = cut.rfind(" ")
    if space > limit // 2:
        return cut[:space].rstrip()
    return cut
