"""Tests for argus.export.translator — template matching and rendering.

These are invariants the production emails depend on:
  * Every template key built by build_template_key must exist in TEMPLATES.
  * No template short exceeds the subject-line length limit.
  * Rendered output never contains an unresolved '{placeholder}' or
    the '[REVIEW]' tag when a template matches.
"""

from __future__ import annotations

import re

import pytest

from argus.export.templates import TEMPLATES
from argus.export.translator import (
    MAX_SHORT_LENGTH,
    REVIEW_TAG,
    build_template_key,
    translate_finding,
)


_PLACEHOLDER_RE = re.compile(r"\{[a-z_]+\}")


def _f(**kw) -> dict:
    base = {
        "id": "X-001",
        "module": "",
        "category": "",
        "severity": "INFO",
        "title": "",
        "evidence": "",
    }
    base.update(kw)
    return base


# ──────────────────────────────────────────────────────────────────────
# Coverage invariant: every key the pipeline emits must resolve.
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("finding,expected_key", [
    (_f(module="shodan_lookup", title="MySQL offen auf Port 3306"), "shodan:mysql"),
    (_f(module="shodan_lookup", title="FTP Port 21"), "shodan:ftp"),
    (_f(module="shodan_lookup", title="PostgreSQL Port 5432"), "shodan:postgresql"),
    (_f(module="shodan_lookup", title="Redis offen"), "shodan:redis"),
    (_f(module="shodan_lookup", title="MongoDB offen"), "shodan:mongodb"),
    (_f(module="shodan_lookup", title="RDP Port 3389"), "shodan:rdp"),
    (_f(module="shodan_lookup", title="SSH Port 22"), "shodan:ssh"),
    (_f(module="shodan_lookup", title="Telnet Port 23"), "shodan:telnet"),
    (_f(module="shodan_lookup", title="SMB öffentlich erreichbar auf 1.1.1.1:445"), "shodan:smb"),
    (_f(module="shodan_lookup", title="MSSQL öffentlich erreichbar auf 1.1.1.1:1433"), "shodan:mssql"),
    (_f(module="shodan_lookup", title="VNC öffentlich erreichbar auf 1.1.1.1:5900"), "shodan:vnc"),
    (_f(module="shodan_lookup", title="Elasticsearch öffentlich erreichbar"), "shodan:elasticsearch"),
    (_f(module="shodan_lookup", title="Memcached öffentlich erreichbar"), "shodan:memcached"),
    (_f(module="shodan_lookup", id="SHO-003", title="Veraltetes Betriebssystem: Windows 7"), "shodan:outdated_os"),
    (_f(module="shodan_lookup", id="SHO-002", title="CVE aktiv"), "shodan:cve"),
    (_f(module="shodan_lookup", id="SHO-002-AGG", title="3 ungepatchte CVEs"), "shodan:cve"),
    (_f(module="shodan_lookup", id="SHO-004", title="19 offene Ports"), "shodan:many_ports"),
    (_f(module="exchange", id="EX-003", title="/ecp"), "exchange:ecp_powershell"),
    (_f(module="exchange", id="EX-004", title="/PowerShell"), "exchange:ecp_powershell"),
    (_f(module="exchange", id="EX-010", title="8 Endpoints"), "exchange:multiple_endpoints"),
    (_f(module="exchange", id="EX-005", title="Basic Auth"), "exchange:basic_auth"),
    (_f(module="exchange", id="EX-001", title="EOL"), "exchange:eol"),
    (_f(module="exchange", id="EX-007", title="AD Domain geleakt"), "exchange:ad_domain_leak"),
    (_f(module="exchange", id="EX-008", title="Server-FQDN geleakt"), "exchange:fqdn_leak"),
    (_f(module="exchange", id="EX-009", title="Hostname-Leak"), "exchange:hostname_leak"),
    (_f(module="file_exposure", title="/web.config öffentlich"), "file:webconfig"),
    (_f(module="file_exposure", title="/.env exponiert"), "file:env"),
    (_f(module="file_exposure", title="/.htpasswd offen"), "file:htpasswd"),
    (_f(module="file_exposure", title="/.htaccess offen"), "file:htaccess"),
    (_f(module="file_exposure", title="/.git exponiert"), "file:git"),
    (_f(module="file_exposure", title="/composer.json öffentlich"), "file:composer"),
    (_f(module="file_exposure", title="/package.json öffentlich"), "file:package_json"),
    (_f(module="file_exposure", title="/phpinfo.php"), "file:phpinfo"),
    (_f(module="file_exposure", title="docker-compose.yml"), "file:docker"),
    (_f(module="file_exposure", title="Backup-Datei"), "file:backup"),
    (_f(module="file_exposure", title="SQL-Dump"), "file:sqldump"),
    (_f(module="dns_intel", id="DNS-006", title="Kein DMARC"), "email:no_dmarc"),
    (_f(module="dns_intel", id="DNS-004", title="DMARC p=none"), "email:dmarc_none"),
    (_f(module="dns_intel", id="DNS-002", title="Kein SPF"), "email:no_spf"),
    (_f(module="dns_intel", id="DNS-001", title="SPF ~all"), "email:spf_weak"),
    (_f(module="dns_intel", id="DNS-003", title="Kein DKIM"), "email:no_dkim"),
    (_f(module="dns_intel", id="DNS-005", title="sp=none"), "email:dmarc_subdomain_none"),
    (_f(module="dns_intel", id="DNS-007", title="Kein MTA-STS"), "email:no_mta_sts"),
    (_f(module="dns_intel", id="DNS-008", title="Kein DANE"), "email:no_dane"),
    (_f(module="dns_intel", id="DNS-010", title="SPF Limit"), "email:spf_too_many_lookups"),
    (_f(module="zone_transfer", id="DNS-AXFR", title="AXFR offen"), "email:zone_transfer"),
    (_f(module="credential_exposure", id="CRED-001", title="leak"), "cred:hibp_password"),
    (_f(module="credential_exposure", id="CRED-002", title="leak"), "cred:hibp_recent"),
    (_f(module="credential_exposure", id="CRED-004", title="GF-Mail"), "cred:hibp_gf"),
    (_f(module="credential_exposure", id="CRED-005", title="leak"), "cred:hibp_multiple"),
    (_f(module="credential_exposure", id="CRED-003", title="leak"), "cred:hibp_metadata"),
    (_f(module="admin_panel", title="phpMyAdmin"), "admin:phpmyadmin"),
    (_f(module="admin_panel", title="Adminer"), "admin:adminer"),
    (_f(module="admin_panel", title="cPanel"), "admin:cpanel"),
    (_f(module="admin_panel", title="Plesk"), "admin:plesk"),
    (_f(module="admin_panel", title="Webmail"), "admin:webmail"),
    (_f(module="admin_panel", title="WordPress-Login"), "admin:wordpress"),
    (_f(module="admin_panel", title="TYPO3 Backend"), "admin:typo3"),
    (_f(module="admin_panel", title="Joomla Admin"), "admin:joomla"),
    (_f(module="admin_panel", title="Drupal Admin"), "admin:drupal"),
    (_f(module="tls_analysis", title="TLS 1.0 aktiv"), "tls:tls10"),
    (_f(module="tls_analysis", title="TLS 1.1 aktiv"), "tls:tls11"),
    (_f(module="source_maps", title="Source Map"), "srcmap:exposed"),
    (_f(module="google_dorking", title="Vertrauliche PDFs"), "dork:confidential_pdfs"),
    (_f(module="google_dorking", title="Excel-Dateien"), "dork:excel"),
    (_f(module="google_dorking", title="Admin indexiert"), "dork:admin_indexed"),
    (_f(module="google_dorking", title="CI/CD indexiert"), "dork:cicd_indexed"),
    (_f(module="google_dorking", title="Entwicklungstools indexiert"), "dork:devtools_indexed"),
    (_f(module="subdomain_discovery", id="SUB-004", title="db.*"), "sub:database"),
    (_f(module="subdomain_discovery", id="SUB-002", title="admin.*"), "sub:admin"),
    (_f(module="subdomain_discovery", id="SUB-001", title="staging.*"), "sub:staging"),
    (_f(module="tech_fingerprint", id="TECH-001", title="Nginx: 1.14"), "tech:outdated"),
    (_f(module="tech_fingerprint", id="TECH-002", title="Server-Header leak"), "tech:version_leak"),
    (_f(module="wayback_machine", id="WB-001", title="Archiv live"), "wayback:live_sensitive"),
    (_f(module="wayback_machine", id="WB-002", title="Archiv"), "wayback:archived_sensitive"),
    (_f(module="wayback_machine", id="WB-003", title="17 sensitive URLs"), "wayback:many_sensitive"),
    (_f(module="http_headers", id="HDR-COOKIE-001", title="Cookie insecure"), "cookie:insecure"),
    (_f(module="cloud_buckets", id="CLOUD-001", title="Bucket offen"), "cloud:public_bucket"),
    (_f(module="github_secrets", title="Privater Schlüssel"), "github:private_key"),
    (_f(module="github_secrets", title="API-Key"), "github:api_key"),
    (_f(module="github_secrets", title="Datenbank-Credentials"), "github:db_creds"),
    (_f(module="github_secrets", title="AWS Access Key"), "github:aws_key"),
    (_f(module="github_secrets", title="Passwort gefunden"), "github:password"),
])
def test_build_template_key_resolves(finding, expected_key):
    assert build_template_key(finding) == expected_key
    assert expected_key in TEMPLATES, f"key {expected_key!r} missing from TEMPLATES"


# ──────────────────────────────────────────────────────────────────────
# Template invariants (conversion-critical)
# ──────────────────────────────────────────────────────────────────────

def test_all_short_fields_under_limit():
    too_long = [
        (k, v["short"]) for k, v in TEMPLATES.items() if len(v["short"]) > MAX_SHORT_LENGTH
    ]
    assert not too_long, f"template shorts exceed {MAX_SHORT_LENGTH} chars: {too_long}"


def test_all_templates_have_short_and_what():
    for key, v in TEMPLATES.items():
        assert "short" in v and v["short"], f"{key} missing short"
        assert "what" in v and v["what"], f"{key} missing what"


def test_no_english_leak_in_what_fields():
    # Soft linter: some common English words that shouldn't appear in body copy.
    english_red_flags = [" the ", " and ", " is ", " your ", " are "]
    for key, v in TEMPLATES.items():
        what_lower = v["what"].lower()
        for word in english_red_flags:
            assert word not in what_lower, f"{key} contains English: {word}"


# ──────────────────────────────────────────────────────────────────────
# Rendering behavior
# ──────────────────────────────────────────────────────────────────────

def test_render_hibp_password_substitutes_email():
    scan = {"domain": "laseroptik.com", "findings": []}
    f = _f(
        module="credential_exposure", id="CRED-001",
        category="credential_exposure", severity="KRITISCH",
        title="info@laseroptik.com in 1 Leck",
        evidence="info@laseroptik.com found in breach",
    )
    t = translate_finding(f, scan)
    assert "info@laseroptik.com" in t["what"]
    assert REVIEW_TAG not in t["what"]
    assert not _PLACEHOLDER_RE.search(t["what"])


def test_render_hibp_falls_back_to_info_at_domain():
    scan = {"domain": "acme.com", "findings": []}
    f = _f(
        module="credential_exposure", id="CRED-001",
        category="credential_exposure", severity="KRITISCH",
        title="Passwort in 1 Leck",
        evidence="no email here",
    )
    t = translate_finding(f, scan)
    assert "info@acme.com" in t["what"]


def test_render_cve_uses_aggregated_count():
    scan = {"domain": "x.com", "findings": []}
    f = _f(
        id="SHO-002-AGG", module="shodan_lookup",
        category="infrastructure", severity="KRITISCH",
        title="12 ungepatchte CVEs auf 1.2.3.4",
        cve_ids=["CVE-2024-0001", "CVE-2024-0002"],
    )
    t = translate_finding(f, scan)
    assert "2" in t["what"]  # cve_count derived from cve_ids list
    assert "CVE-2024-0001" in t["what"]
    assert not _PLACEHOLDER_RE.search(t["what"])


def test_unknown_finding_falls_through_to_review_tag():
    scan = {"domain": "x.com", "findings": []}
    f = _f(module="nonexistent_module", title="Some Thing", description="raw desc")
    t = translate_finding(f, scan)
    assert t["what"].startswith(REVIEW_TAG)


def test_dmarc_subdomain_placeholder_resolves():
    scan = {"domain": "acme.com", "findings": []}
    f = _f(module="dns_intel", id="DNS-005", severity="HOCH",
           category="email_security", title="sp=none")
    t = translate_finding(f, scan)
    assert "mail.acme.com" in t["what"]
    assert not _PLACEHOLDER_RE.search(t["what"])
